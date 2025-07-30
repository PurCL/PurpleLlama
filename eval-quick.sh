#!/bin/bash
MODEL_NAME=$1
PARAM=$2
VLLM_PORT=$3

# if 4 params, host is provided
if [ $# -eq 4 ]; then
   HOST=$4
else
   HOST=""
fi

DATASETS=$PWD/CybersecurityBenchmarks/datasets
TOP_N=20
CWE_ID=prosec-subset
TEMPERATURE=0.8
TOP_K=50
VLLM_TOKEN=prosectoken

RESPONSE_DIR=$DATASETS/instruct-response/$CWE_ID
STAT_DIR=$DATASETS/instruct-stat/$CWE_ID

echo "Starting Eval for $MODEL_NAME on port $VLLM_PORT"

if [ ! -d "$RESPONSE_DIR" ]; then
   mkdir -p "$RESPONSE_DIR"
fi

if [ ! -d "$STAT_DIR" ]; then
   mkdir -p "$STAT_DIR"
fi

mkdir -p eval-log

vllm serve $MODEL_NAME --dtype bfloat16 --api-key $VLLM_TOKEN --swap_space 32 --port $VLLM_PORT &
PID=$!
sleep 90

# Run the evaluation
python -m CybersecurityBenchmarks.benchmark.run \
   --benchmark=instruct \
   --prompt-path="$DATASETS/instruct/instruct-$CWE_ID.json" \
   --response-path="$RESPONSE_DIR/top$TOP_N-$PARAM.json" \
   --stat-path="$STAT_DIR/top$TOP_N-$PARAM.json" \
   --llm-under-test="VLLM::$MODEL_NAME::$HOST::$VLLM_PORT::$VLLM_TOKEN" \
   --num-queries-per-prompt=$TOP_N \
   --temperature=$TEMPERATURE \
   --top_k=$TOP_K \
   --run-llm-in-parallel > eval-log/eval-quick-$PARAM-$CWE_ID.log 2>&1


kill $PID &

sleep 30

kill -9 $PID