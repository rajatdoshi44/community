from fastapi import FastAPI, Request, Response, HTTPException
import httpx

app = FastAPI(title="Community API Gateway")

# Internal microservices ke ports ka map
SERVICES = {
    "members": "http://localhost:8005",
    "family-units": "http://localhost:8002",
    "family-tracker": "http://localhost:8007",
    "parent-child": "http://localhost:8003",
}

# Global async client taaki connections reuse ho sakein
client = httpx.AsyncClient()


@app.get("/")
async def health_check():
    return {"status": "Community API Gateway is healthy"}


@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(service_name: str, path: str, request: Request):
    # Check karna ki service hamare map mein hai ya nahi
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found on Gateway")

    # Target URL construct karna (eg: http://localhost:8001/get-all-members)
    target_url = f"{SERVICES[service_name]}/{service_name}/{path}"
    print(target_url)
    # Incoming request se body aur headers nikalna
    body = await request.body()
    headers = dict(request.headers)

    # 'host' header remove karna zaroori hai, warna target server conflict dega
    headers.pop("host", None)

    try:
        # Microservice ko request forward karna
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
        )

        # Wapas aayi hui response ko React Native app ko return karna
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Target service is down: {str(exc)}")


if __name__ == "__main__":
    main()
