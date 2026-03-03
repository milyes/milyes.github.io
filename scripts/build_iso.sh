#!/bin/bash
set -e
BASE_ISO="debian-live.iso"
WORKDIR="live-iso-working"
OUTPUT_ISO="NetSecurePro_IA22.iso"
NSP_FILE="iso.nsp"
mkdir -p ${WORKDIR}/mnt
sudo mount -o loop ${BASE_ISO} ${WORKDIR}/mnt
rsync -a ${WORKDIR}/mnt/ ${WORKDIR}/extract/
sudo umount ${WORKDIR}/mnt
mkdir -p ${WORKDIR}/extract/extensions
cp ${NSP_FILE} ${WORKDIR}/extract/extensions/
cd ${WORKDIR}/extract
genisoimage -o ../${OUTPUT_ISO} -rational-rock -volid "NSP_Live" -cache-inodes -joliet   -boot-info-table -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot   -boot-load-size 4 -boot-load-seg 07C0 .
echo "ISO generated: ${WORKDIR}/${OUTPUT_ISO}"
