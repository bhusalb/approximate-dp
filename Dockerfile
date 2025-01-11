FROM ubuntu:22.04
COPY . /home/ubuntu/approx-dp
WORKDIR /home/ubuntu/approx-dp
RUN apt-get update
RUN apt install -y apt-transport-https curl gnupg
RUN apt update
RUN apt install -y libgmp-dev libmpfr-dev make autoconf libtool-bin
RUN apt install -y --no-install-recommends build-essential
RUN apt-get install -y --no-install-recommends bison coinor-libclp-dev g++ libfl-dev libgmp-dev libnlopt-cxx-dev libpython3-dev pkg-config python3-distutils python3-minimal zlib1g-dev
RUN apt install -y cmake
RUN apt install -y libmpfr-dev 
RUN apt install -y python3-pip git
RUN git clone https://github.com/flintlib/flint.git
RUN cd flint && ./bootstrap.sh && ./configure && make && make install
RUN cd /home/ubuntu/approx-dp/ && pip3 install -r requirements.txt
CMD ["/bin/bash"]