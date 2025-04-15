
# DpApprox 

An automated and integrated tool for proving and disproving Differential Privacy with gaussian distributions and laplace distributions.

# Install via Docker
Due to the multiple dependencies of this project, it is much easier to install inside a docker container. 

In the project root directory, run:

```bash
docker build . -t dpapprox
docker run --rm -it dpapprox
```

# Usage
Run `python3 src/main.py -h` you will see the following help message:

```
usage: main.py [-h] --file FILE --eps EPS [--delta DELTA] [--deps DEPS] [--k K] [--input INPUT] [--debug] [--characterize] [--regular] [--output OUTPUT] [--prec PREC]
               [--epriv EPRIV]

Approx DP

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE
  --eps EPS, -e EPS     The value of epsilon.
  --delta DELTA, -d DELTA
                        The value of delta.
  --deps DEPS, -D DEPS  The value of D.
  --k K, -k K           The value of thr.
  --input INPUT, -i INPUT
                        The file path for adjacent pairs.
  --debug, -dd
  --characterize, -c
  --regular, -r
  --output OUTPUT, -o OUTPUT
                        Check for the particular output.
  --prec PREC, -p PREC  The prec for the computation.
  --epriv EPRIV, -ee EPRIV
                        The value of the epsilon priv.
```


Run `python3 src/main.py -f [FILE] -e [eps] -d [delta]` to start analyzing `[FILE]`, the tool will generate a `temp_program` executable containing encoded probabilities for proving or disproving differential privacy.

### Writing Your Own Algorithm

Most of the syntax in DpApprox is the very simple: 
1. Program must have INPUT_SIZE constant and OUTPUT array.

2. You can define two types of variables, NUMERIC and RANDOM variables. 

3. You can use IF THEN statement or IF THEN ELSE statement. 

4. You can sample from `gauss` or `lap`.
Let's look at an example `svt` algorithm in `examples/svt/example_1.dip`.

```C
INPUTSIZE 1;
RANDOM TH = gauss(eps/2, 0);
OUTPUT = [0];
    
RANDOM Q0 = gauss(eps/4, INPUT[0]);
IF Q0 < TH THEN {
    OUTPUT[0] = 1;
}
```


[//]: # (# License)

[//]: # ([MIT]&#40;./LICENSE&#41;.)
