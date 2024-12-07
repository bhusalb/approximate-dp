FROM ubuntu:22.04
COPY . /home/ubuntu/approx-dp
WORKDIR /home/ubuntu/approx-dp
RUN apt-get update
RUN apt install apt-transport-https curl gnupg -y 


RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
RUN mv bazel-archive-keyring.gpg /usr/share/keyrings
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
RUN apt update

RUN apt install -y --no-install-recommends build-essential
RUN apt-get install -y --no-install-recommends bison coinor-libclp-dev g++ libfl-dev libgmp-dev libnlopt-cxx-dev libpython3-dev pkg-config python3-distutils python3-minimal zlib1g-dev

RUN apt install -y cmake
RUN apt install -y libmpfr-dev 
RUN apt install -y python3-pip
RUN apt install -y  bazel-5.1.0


RUN cd /home/ubuntu/approx-dp/ && pip3 install -r requirements.txt

CMD ["/bin/bash"]