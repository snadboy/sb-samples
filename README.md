# SB Samples

Sample projects using SB libraries.

## Projects

### Notion

- **TV Shows**: A sample application that manages TV show information in Notion databases.
  - Uses `sb-notion` for database interaction
  - Demonstrates async API usage
  - Shows class generation from database schema

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/snadboy/sb-samples.git
   cd sb-samples
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix:
   source .venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Running Examples

### TV Shows Example
```bash
cd notion/tv_shows
python example_async.py
```

## Development

- Format code: `black .`
- Sort imports: `isort .`
- Lint code: `flake8`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
