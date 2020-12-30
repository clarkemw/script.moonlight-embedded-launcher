# Moonlight embedded for libreelec
# See https://github.com/clarkemw/moonlight-embedded-launcher for installation instructions
# See https://github.com/irtimmer/moonlight-embedded/wiki/Usage for command instructions
#
# Run syntax: 
#	docker run -it -v moonlight-home:/home/moonlight-user \
#	-v /var/run/dbus:/var/run/dbus --device /dev/vchiq:/dev/vchiq \
#	moonlight [action] (options) [host]
#

FROM raspbian/stretch

RUN echo "deb http://archive.itimmer.nl/raspbian/moonlight stretch main" >> /etc/apt/sources.list \
	&& wget http://archive.itimmer.nl/itimmer.gpg \
	&& apt-key add itimmer.gpg \
	&& apt-get update \
	&& apt-get install -y moonlight-embedded

# Create directory for saved data
ENV HOME /home/moonlight-user

RUN mkdir -p $HOME

# $HOME will be exposed as a docker mount so the data is persistent
VOLUME $HOME

EXPOSE 80

ENTRYPOINT [ "/usr/bin/moonlight" ]
