# Project goal: zeroth try exploring bluesky firehose


# Quick run:

```
# v0.0
dataset_tag=random_100
uv run python sample_firehose.py --dataset_tag "random_100" --sample-rate 0.1 --max-posts 100
uv run python derive_fields.py $dataset_tag
```
