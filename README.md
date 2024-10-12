# 🪶 journal

## Configuration

### Environment variables

#### DATABASE_URL

Only Postgres or derivant are supported. Default value is `postgres://postgres:postgres@localhost:5432/journal`.

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