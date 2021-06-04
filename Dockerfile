
FROM python:3.10.0b1-buster

RUN mkdir -p /root/shell
COPY .pysh.py /root/
COPY src/* /root/shell/

CMD [ "python", "/root/shell/pysh.py" ]