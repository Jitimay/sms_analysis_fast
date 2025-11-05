# ProofOfFace Substrate Node Dockerfile
FROM paritytech/ci-linux:production as builder

WORKDIR /proofofface

# Copy source code
COPY . .

# Install Rust and dependencies
RUN rustup default stable && \
    rustup target add wasm32-unknown-unknown && \
    rustup component add rust-src

# Build the node
RUN cargo build --release

# Runtime stage
FROM ubuntu:20.04

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the binary
COPY --from=builder /proofofface/target/release/proofofface-node /usr/local/bin/

# Create user
RUN useradd -m -u 1000 -U -s /bin/sh -d /proofofface proofofface && \
    mkdir -p /data /proofofface/.local/share && \
    chown -R proofofface:proofofface /data && \
    ln -s /data /proofofface/.local/share/proofofface-node

USER proofofface

# Expose ports
EXPOSE 30333 9933 9944 9615

VOLUME ["/data"]

ENTRYPOINT ["/usr/local/bin/proofofface-node"]