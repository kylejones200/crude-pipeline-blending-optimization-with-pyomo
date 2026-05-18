# Crude Pipeline Blending Optimization with Pyomo

Published: 2025-07-14
Medium: [https://medium.com/@kyle-t-jones/crude-pipeline-blending-optimization-with-pyomo-d7f6c725f594](https://medium.com/@kyle-t-jones/crude-pipeline-blending-optimization-with-pyomo-d7f6c725f594)

## Business context

Blending crude oil is not a guessing game. Midstream companies do it to meet contractual specs and maximize margin. Each barrel blended below spec costs money. Each unnecessary premium barrel blended in gives away value. A well-built optimization model ensures the right blend goes into the pipe every day.

This article walks through a working example of crude blending using Pyomo in Python. We use API gravity and sulfur as constraints. The goal is to minimize cost while meeting product specs. No proprietary data. No black boxes. Everything runs locally and transparently.

You manage a tank farm with multiple crude streams. Incoming deliveries vary each week. Your customers expect output that meets a minimum API gravity and a maximum sulfur level. You want to mix available barrels to meet that spec at the lowest cost.

## About

Place the code for this article in this repository.
The original article export is saved as `article.md`.

## Files

Add your `.ipynb`, `.py`, `.yaml`, `.js`, `.ts`, or other project files here.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).