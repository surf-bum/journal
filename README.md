# 🪶 journal

## Configuration

### Environment variables

| Environment URL      | Default                                                   |
| -------------------- | --------------------------------------------------------- |
| DATABASE_URL         | postgres://postgres:postgres@localhost:5432/journal       |
| SECRET_KEY           | my-secret-key                                             |

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

## Deployment

Single instance running inside a Docker container. 

Application served by gunicorn, worker class is "sync", number of workers is double the number of "logical" CPU cores.