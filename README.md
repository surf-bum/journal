# 🪶 journal

## Configuration

### Environment variables

#### DATABASE_URL
#### SECRET_KEY

## Dependencies

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

## Testing

### Integration

#### Dependencies

    playwright install chromium

#### Run headless

    pytest --browser chromium --headed

#### Run headed

    pytest --browser chromium --headed

#### Debug

    PW_DEBUG=1 pytest --browser chromium