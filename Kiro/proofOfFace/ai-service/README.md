# ProofOfFace AI Service

A Flask-based REST API service for face recognition and biometric processing, designed to work with the ProofOfFace blockchain identity verification system.

## Features

- **Face Detection & Recognition**: Advanced face detection using the `face_recognition` library
- **Biometric Hash Generation**: Deterministic hash generation from face encodings
- **Encryption Support**: Secure encryption/decryption of face encodings
- **Image Quality Assessment**: Automatic image quality scoring
- **RESTful API**: Clean REST endpoints for integration
- **Docker Support**: Containerized deployment
- **Production Ready**: Gunicorn WSGI server with proper error handling

## API Endpoints

### Health Check
```
GET /health
```
Returns service status and configuration information.

### Process Face
```
POST /process-face
Content-Type: multipart/form-data
```
Upload an image file to extract face biometric data.

**Request:**
- `image`: Image file (PNG, JPG, JPEG, GIF, BMP)

**Response:**
```json
{
  "success": true,
  "biometric_hash": "sha256_hash_of_face_encoding",
  "encrypted_face_encoding": "encrypted_base64_encoding",
  "quality_score": 0.85,
  "processing_time": 1.234,
  "face_location": [top, right, bottom, left]
}
```

### Get Configuration
```
GET /config
```
Returns current service configuration (non-sensitive data only).

## Installation

### Local Development

1. **Clone the repository:**
```bash
git clone <repository_url>
cd ai-service
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables:**
```bash
export FLASK_ENV=development
export SECRET_KEY=your_secret_key_here
export ENCRYPTION_KEY=your_encryption_key_here
```

5. **Run the application:**
```bash
python app.py
```

The service will be available at `http://localhost:5000`

### Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t proofofface-ai .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your_secret_key \
  -e ENCRYPTION_KEY=your_encryption_key \
  proofofface-ai
```

### Docker Compose

```yaml
version: '3.8'
services:
  ai-service:
    build: ./ai-service
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - FACE_RECOGNITION_TOLERANCE=0.6
      - FACE_RECOGNITION_MODEL=large
    volumes:
      - ./uploads:/tmp/proofofface_uploads
    restart: unless-stopped
```

## Configuration

The service can be configured using environment variables:

### Core Settings
- `FLASK_ENV`: Environment mode (`development`, `production`, `testing`)
- `SECRET_KEY`: Flask secret key for session security
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `5000`)

### Face Recognition Settings
- `FACE_RECOGNITION_TOLERANCE`: Matching tolerance (0.0-1.0, default: `0.6`)
- `FACE_RECOGNITION_MODEL`: Model type (`small` or `large`, default: `large`)
- `MAX_IMAGE_SIZE`: Maximum image size in bytes (default: `5242880` = 5MB)

### Security Settings
- `ENCRYPTION_KEY`: Base64-encoded encryption key for face encodings
- `CORS_ORIGINS`: Allowed CORS origins (default: `*` in dev, restricted in prod)

### Logging Settings
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `LOG_FORMAT`: Log format (`json` or `text`)

### Rate Limiting
- `RATE_LIMIT_PER_MINUTE`: API calls per minute per IP (default: `60`)

## Usage Examples

### Python Client Example

```python
import requests

# Process a face image
with open('face_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/process-face',
        files={'image': f}
    )

if response.status_code == 200:
    data = response.json()
    print(f"Biometric Hash: {data['biometric_hash']}")
    print(f"Quality Score: {data['quality_score']}")
else:
    print(f"Error: {response.json()['error']}")
```

### cURL Example

```bash
# Health check
curl http://localhost:5000/health

# Process face image
curl -X POST \
  -F "image=@face_image.jpg" \
  http://localhost:5000/process-face

# Get configuration
curl http://localhost:5000/config
```

### JavaScript/Fetch Example

```javascript
// Process face image
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/process-face', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Biometric Hash:', data.biometric_hash);
        console.log('Quality Score:', data.quality_score);
    } else {
        console.error('Error:', data.error);
    }
});
```

## Architecture

### Project Structure
```
ai-service/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── README.md           # This file
└── utils/
    ├── __init__.py
    ├── face_processor.py  # Face detection and processing
    └── encryption.py      # Encryption utilities
```

### Key Components

1. **Face Processor (`utils/face_processor.py`)**
   - Face detection using HOG or CNN models
   - Face encoding extraction (128-dimensional vectors)
   - Image quality assessment
   - Biometric hash generation

2. **Encryption Manager (`utils/encryption.py`)**
   - Symmetric encryption using Fernet (AES 128)
   - Secure face encoding encryption/decryption
   - Key derivation from passwords

3. **Configuration (`config.py`)**
   - Environment-specific settings
   - Validation and security checks
   - Development/Production configurations

## Security Considerations

### Data Protection
- Face encodings are encrypted before storage/transmission
- Biometric hashes are one-way (cannot reverse to original encoding)
- No raw images are stored permanently
- Secure key management required

### API Security
- CORS protection with configurable origins
- Rate limiting to prevent abuse
- Input validation and sanitization
- Error handling without information leakage

### Production Deployment
- Run as non-root user in containers
- Use environment variables for secrets
- Enable HTTPS in production
- Monitor and log security events

## Performance

### Optimization Tips
1. **Model Selection**: Use `small` model for faster processing, `large` for better accuracy
2. **Image Size**: Resize large images before processing
3. **Caching**: Implement Redis caching for repeated requests
4. **Load Balancing**: Use multiple worker processes with Gunicorn

### Benchmarks
- **Small Model**: ~0.5-1.0 seconds per image
- **Large Model**: ~1.0-2.0 seconds per image
- **Memory Usage**: ~200-500MB per worker process
- **Throughput**: ~10-30 requests/second (depending on hardware)

## Troubleshooting

### Common Issues

1. **Face Not Detected**
   - Ensure good image quality (lighting, resolution)
   - Check face is clearly visible and not obscured
   - Try different angles or lighting conditions

2. **Low Quality Score**
   - Improve image lighting and focus
   - Use higher resolution images
   - Ensure face takes up significant portion of image

3. **Memory Issues**
   - Reduce number of Gunicorn workers
   - Use `small` face recognition model
   - Implement image size limits

4. **Slow Processing**
   - Use `small` model for faster processing
   - Resize images before processing
   - Consider GPU acceleration (requires additional setup)

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export FLASK_ENV=development
python app.py
```

### Health Monitoring

The service provides a health check endpoint that returns:
- Service status
- Configuration information
- Environment details
- Processing capabilities

## Integration with ProofOfFace

This AI service is designed to integrate with the ProofOfFace blockchain system:

1. **Identity Registration**: Process face images to generate biometric hashes
2. **Identity Verification**: Compare face images against stored encodings
3. **Dispute Evidence**: Process evidence images for dispute resolution

### Blockchain Integration Flow

1. User uploads face image to AI service
2. AI service processes image and returns biometric hash
3. Frontend submits hash to Substrate blockchain
4. Blockchain stores hash and emits events
5. AI service can verify faces against blockchain data

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app.py utils/

# Lint code
flake8 app.py utils/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks
5. Submit pull request

## License

This project is part of the ProofOfFace identity verification system.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue in the repository
4. Contact the development team

---

**Note**: This service handles biometric data. Ensure compliance with relevant privacy laws and regulations in your jurisdiction.