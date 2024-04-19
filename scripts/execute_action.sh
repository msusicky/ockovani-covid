#!/bin/bash
curl -X POST "https://api.github.com/repos/msusicky/ockovani-covid/actions/workflows/$1/dispatches" -H "Authorization: token $GH_TOKEN" -H "Accept: application/vnd.github.v3+json" -d '{ "ref": "main" }'
