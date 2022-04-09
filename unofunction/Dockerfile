FROM --platform=linux/amd64 unofunction/libreoffice as libreoffice


FROM public.ecr.aws/lambda/python:3.9

# LibreOffice
COPY --from=libreoffice /opt/libreoffice /opt/libreoffice
COPY --from=libreoffice /usr/lib64 /usr/lib64
ENV LIBREOFFICE_PATH=/opt/libreoffice/program/soffice.bin

# Fonts
COPY --from=libreoffice /etc/fonts /etc/fonts
COPY --from=libreoffice /usr/include/X11/fonts /usr/include/X11/fonts
COPY --from=libreoffice /usr/share/fonts /usr/share/fonts

# Unofunction
COPY convert.py .
COPY handler.py .

CMD [ "handler.handler" ]
