#!/bin/bash
NSP_SRC="iso.nsp"
INSTALL_DIR="/opt/netsecurepro/extensions"
sudo mkdir -p ${INSTALL_DIR}
sudo cp ${NSP_SRC} ${INSTALL_DIR}/
sudo unzip -o ${INSTALL_DIR}/iso.nsp -d /opt/netsecurepro/vision_core/
sudo chmod +x /opt/netsecurepro/vision_core/run_nsp.sh
echo "Installation complete."
