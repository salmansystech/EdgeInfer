# Sample Models

Small models for trying EdgeInfer without bringing your own.

| File | Precision | Parameters | Description |
|---|---|---|---|
| `hello_world_float.tflite` | FLOAT32 | 321 | Predicts sin(x) with three fully connected layers |
| `hello_world_int8.tflite` | INT8 | 321 | The same model, quantized to 8-bit integers |

```bash
python main.py analyze --model examples/sample-models/hello_world_int8.tflite --hardware esp32
```

These models come from the TensorFlow Lite Micro
[hello_world example](https://github.com/tensorflow/tflite-micro/tree/main/tensorflow/lite/micro/examples/hello_world)
and are licensed under the Apache License 2.0. Copyright The TensorFlow Authors.
