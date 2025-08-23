# Approximate Algorithms for Verifying Differential Privacy with Gaussian Distributions

<p align="center">
<a href="https://doi.org/10.5281/zenodo.16930792"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.16930793.svg" alt="DOI"></a>
</p>


This repository contains the artifact for our CCS 2025 paper:  
"Approximate Algorithms for Verifying Differential Privacy with Gaussian Distributions."

The tool, DpApprox, automatically verifies whether algorithms written in ourlang are:
- Differentially private
- Not differentially private
- Or unresolved (inconclusive)

It is implemented in Python and C++, and leverages:
- PLY – program parsing
- igraph – graph-based state representation
- FLINT – efficient integral computation

---

## Download

You can access the artifact in multiple ways:

- GitHub (latest development version):
    git clone https://github.com/bhusalb/approximate-dp.git
    cd approximate-dp

- Zenodo (archived release for CCS 2025): [DOI link here]

- DockerHub (pre-built image) (optional if available):
    docker pull bhusalb/dpapprox

---

## Requirements

- Hardware:
  - Tool: 4 GB RAM
  - Benchmarking: 16 GB RAM

- Software:
  - Unix-like environment (recommended)
  - Docker
  - Git
  - FLINT library

---

## Installation

Build the Docker container:
    docker build . -t dpapprox

Run the container:
    docker run --rm -it dpapprox

---

## Basic Usage

Check options:
    python3 src/main.py --help

Example: analyze examples/svt/example_1.dip
    python3 src/main.py -f examples/svt/example_1.dip -e 0.5
    # Output: { "DP": 1 }

---

## Benchmarks

Benchmarks include:
- SVT variants (Gaussian, Laplace, mixed) → examples/svt*
- NoisyMax/NoisyMin (Gaussian & Laplace) → examples/noisy_*
- k-minmax & m-Range (Gaussian & Laplace) → examples/kminmax*, examples/mrange*

Reproduce paper results:

    # Optimized benchmarks
    python3 scripts/benchmark.py

    # Unoptimized benchmarks
    python3 scripts/benchmark_unoptimized.py

    # Generate Tables 1 & 2
    python3 scripts/table_generator.py

    # Generate Figure 3
    python3 scripts/plot_generator.py

---

## Writing Programs in DiPGauss

Rules:
- Must include INPUTSIZE constant and OUTPUT array
- Variables: NUMERIC or RANDOM
- Control: IF THEN or IF THEN ELSE
- Sampling: gauss(inv_sigma, mean) or lap(inv_scale, mean)

Example:

    INPUTSIZE 1;
    RANDOM TH = gauss(eps/2, 0);
    OUTPUT = [0];

    RANDOM Q0 = gauss(eps/4, INPUT[0]);
    IF Q0 < TH THEN {
        OUTPUT[0] = 1;
    }

---

[//]: # (## Citation)

[//]: # ()
[//]: # (If you use this artifact in your research, please cite our CCS 2025 paper:)

[//]: # ()
[//]: # (    @inproceedings{bhusal2025approximate,)

[//]: # (      title={Approximate Algorithms for Verifying Differential Privacy with Gaussian Distributions},)

[//]: # (      author={Bhusal, Bishnu and Chadha, Rohit and Sistla, A. Prasad and Viswanathan, Mahesh},)

[//]: # (      booktitle={Proceedings of the 2025 ACM SIGSAC Conference on Computer and Communications Security},)

[//]: # (      year={2025},)

[//]: # (      publisher={ACM})

[//]: # (    })

[//]: # ()
[//]: # (---)

[//]: # (## License)

[//]: # ()
[//]: # (This project is licensed under the MIT License - see the LICENSE file for details.)
