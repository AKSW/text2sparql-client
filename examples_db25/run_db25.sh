#!/usr/bin/env bash
# @(#) run ask, query and evaluate for all questions and responses
# Use the unofficial bash strict mode: http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail; export FS=$'\n\t'

API_NAME=${2:-}
API_URL=${1:-}

echo "Running ask, query and evaluate for all questions and responses for $API_NAME at $API_URL"
text2sparql ask -o "${API_NAME}_db25_answers.json" --answers-db "${API_NAME}_db25_answers.db" --retries-log "${API_NAME}_db25_retries.log" questions_db25.yml "${API_URL}"
text2sparql query -o "${API_NAME}_db25_pred_result_set.json" -a "${API_NAME}_db25_answers.json" -l "['en', 'es']" -e "http://141.57.8.18:9081/sparql" questions_db25.yml
text2sparql evaluate -o "${API_NAME}_db25_results.json" -l "['en', 'es']" "${API_NAME}" db25_true_result_set.json "${API_NAME}_db25_pred_result_set.json"
