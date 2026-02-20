#!/usr/bin/env python3
# vim: foldmethod=marker foldmarker={{{,}}}

import requests
from . import *

con = open_AImodels_db(deleteIfExists = True)

def intOrNone(d, k): # {{{
    v = d.get(k)
    return int(v) if v is not None else None
# }}}

def floatOrNone(d, k): # {{{
    v = d.get(k)
    return float(v) if v is not None else None
# }}}

# {{{ Create schema
con.execute('''
create table provider(
    id   text primary key,
    name text,
    npm  text,
    env  text,
    api  text,
    doc  text
)''')

con.execute('''
create table model(
   id                text,
   name              text,
   provider          text    not null references provider,
   family            text,
   open_weights      integer not null check (open_weights in (0, 1)), --  Are trained weights are publicly available?
   status            text    check (status in ('alpha', 'beta', 'deprecated')),
   rel_dt            text    not null,
   upd_dt            text    not null,
   cutoff_dt         text        null,
   --
   attachment        integer not null check (attachment   in (0, 1)),
   reasoning         integer not null check (reasoning    in (0, 1)),
   struct_out        integer     null check (struct_out   in (0, 1)),  -- Structured output supported
   tool_call         integer not null check (tool_call    in (0, 1)),
   temperature       integer     null check (temperature  in (0, 1)),
   --
   lim_ctx           integer     null,
   lim_in            integer     null,
   lim_out           integer     null,
   --
   mod_in            text        null,
   mod_out           text        null,
   --
   cost_input        real        null,
   cost_output       real        null,
   cost_cache_read   real        null,
   cost_cache_write  real        null,
   cost_audio_in     real        null,
   cost_audio_out    real        null,
   cost_reasoning    real        null,
   --
   interleaved text              null, -- TODO
   --
   primary key (id, provider) -- The same model can have different prices in different regions (for example alibaba vs alibaba-cn)
)''')
# }}}

with db.bulk_load(con) as cur: # {{{

   response = requests.get('https://models.dev/api.json')
   data = response.json()  # Nested dict: {provider: {provider_info, "models": {model_id: model_info} } }

   for providerId, provider in data.items(): # {{{

      cur.execute('insert into provider(id, name, npm, env, api, doc) values (?, ?, ?, ?, ?, ?)',
                (provider['id'], provider['name'], provider['npm'], ','.join(provider['env']), provider.get('api', None), provider['doc']))
      for modelId, model in provider['models'].items(): # {{{

        family      = model.get('family'     ,  None)
        interleaved = model.get('interleaved', 'n/a') # TODO: This value seems to be either empty, True, {'field': 'reasoning_content'} or {'field': 'reasoning_details'}
        temperature = intOrNone(model, 'temperature')

        struct_out = None
        if 'structured_output' in model:
            struct_out  = 1 if model['structured_output'] else 0

        mod_in           = ','.join(model.get('modalities', {}).get('input' , []))
        mod_out          = ','.join(model.get('modalities', {}).get('output', []))

        lim_ctx          = int(model['limit']['context'])
        lim_in           = intOrNone(model.get('limit', {}), 'input')
        lim_out          = int(model['limit']['output' ])

        cost_input       = floatOrNone(model.get('cost', {}), 'input'       )
        cost_output      = floatOrNone(model.get('cost', {}), 'output'      )
        cost_cache_read  = floatOrNone(model.get('cost', {}), 'cache_read'  )
        cost_cache_write = floatOrNone(model.get('cost', {}), 'cache_write' )
        cost_reasoning   = floatOrNone(model.get('cost', {}), 'reasoning'   )
        cost_audio_in    = floatOrNone(model.get('cost', {}), 'input_audio' )
        cost_audio_out   = floatOrNone(model.get('cost', {}), 'output_audio')

        open_weights     = 1 if model['open_weights'] else 0
        status           = model.get('status', None)

        cutoff_dt        = model.get('knowledge', None)


        cur.execute('''insert into model(
                    id, name, provider, family,
                    open_weights,
                    status,
                    rel_dt, upd_dt, cutoff_dt,
                    attachment, reasoning, struct_out, tool_call, temperature,
                    lim_ctx, lim_in, lim_out,
                    mod_in, mod_out,
                    cost_input, cost_output, cost_cache_read , cost_cache_write, cost_audio_in, cost_audio_out, cost_reasoning,
                    interleaved) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
              modelId,
              model['name'        ],
              providerId,
              family,
              open_weights,
              status,
              model['release_date'], model['last_updated'], cutoff_dt,
              model['attachment'  ],
              model['reasoning'   ],
              struct_out,
              model['tool_call'   ],
              temperature,
              lim_ctx, lim_in, lim_out,
              mod_in, mod_out,
              cost_input, cost_output, cost_cache_read, cost_cache_write, cost_audio_in, cost_audio_out, cost_reasoning,
              str(interleaved)
            )
        )
       # }}}
   # }}}

# }}}

