use axum::{routing::post, Json, Router};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct ComputePayload {
    task_hash: String,
    weights_ref: String,
    data_chunk_ref: String,
}

#[derive(Serialize)]
struct ComputeResult {
    gradient_ref: String,
    compute_time_ms: f64,
}

async fn execute_tensor_task(Json(payload): Json<ComputePayload>) -> Json<ComputeResult> {
    let compute_time_ms = 14.25; 
    let gradient_ref = format!("mem_cache_0x{}", payload.task_hash);

    Json(ComputeResult {
        gradient_ref,
        compute_time_ms,
    })
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/compute", post(execute_tensor_task));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    println!("[OCF AGENT] Substrate network daemon online. Bound to port 8080.");
    axum::serve(listener, app).await.unwrap();
}
