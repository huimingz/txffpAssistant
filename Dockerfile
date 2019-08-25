FROM python:3.7

MAINTAINER huimingz kairu_madigan@yahoo.co.jp

RUN mkdir -p /txffp

WORKDIR /txffp

COPY . ./

RUN python setup.py install

ENTRYPOINT ["txffp"]

CMD ["--help"]
