# 🪶 journal

## Configuration

### Environment variables

#### DATABASE_URL

Only Postgres or derivant are supported. Default value is `postgres://postgres:postgres@localhost:5432/journal`.

#### SECRET_KEY

## Development setup

### Dependencies

    pip install -r requirements.txt -r requirements-dev.txt

## Testing

### Integration

#### Dependencies

    playwright install chromium

#### Run headless

    pytest

#### Run headed

    pytest --headed

#### Debug

    PW_DEBUG=1 pytest


### Data layer

#### Make migrations

    piccolo migrations new notes --auto --desc="Adding name column"


#### Forward migrations

    piccolo migrations forwards all


#### Troubleshoot

    piccolo --diagnose