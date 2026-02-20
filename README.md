# AImodelsDB

SQLite database of AI models as fetched from the [models.dev](https://github.com/anomalyco/models.dev) endpoint,
which is maintained by the [anomalyco/models.dev](https://github.com/anomalyco/models.dev) community.

## Installation

```bash
pip install AImodelsDB
```

## Create the database

```bash
python3 -m AImodelsDB.create
```

Then query with:

```bash
sqlite3 ~/.local/share/sqlite-dbs/AImodels.db
```

## Usage

```python
from AImodelsDB import open_AImodels_db

# Get an sqlite3 Connection object to the
# database:
con = open_AImodels_db()
```

## Database Schema

### provider
- `id` (text, primary key)
- `name` (text)
- `npm` (text)
- `env` (text)
- `api` (text)
- `doc` (text)

### model
- `id` (text)
- `name` (text)
- `provider` (text, foreign key)
- `family` (text)
- `open_weights` (integer)
- `status` (text)
- `rel_dt` (text)
- `upd_dt` (text)
- `cutoff_dt` (text)
- `attachment` (integer)
- `reasoning` (integer)
- `struct_out` (integer)
- `tool_call` (integer)
- `temperature` (integer)
- `lim_ctx` (integer)
- `lim_in` (integer)
- `lim_out` (integer)
- `mod_in` (text)
- `mod_out` (text)
- `cost_input` (real)
- `cost_output` (real)
- `cost_cache_read` (real)
- `cost_cache_write` (real)
- `cost_audio_in` (real)
- `cost_audio_out` (real)
- `cost_reasoning` (real)
- `interleaved` (text)
