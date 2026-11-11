# Geely Telemetry para Home Assistant

Integração criada e validada para o **Geely EX2 vendido no Brasil**. Ela exibe sensores comuns do veículo e uma entidade `device_tracker` para GPS. Recebe dados do app pela internet ou lê a central na rede local.

> **Compatibilidade:** a integração e o protocolo foram desenvolvidos para o EX2 brasileiro. Variações de sensores e protocolo por mercado, ano e software podem impedir o funcionamento em versões internacionais ou em outros modelos Geely. Essas combinações não foram validadas.

## Instalação

1. Copie a pasta `geely_telemetry` para `config/custom_components/` no Home Assistant ou instale pelo HACS.
2. Reinicie o Home Assistant e adicione a integração **Geely Telemetry**.
3. Para receber pela internet, escolha **App do carro pela internet**. Para uso local, escolha **Rede local** e informe o endereço e a porta da central.
4. No app instalado na central, permita o acesso à localização quando solicitado.
5. No app, abra **Destino**, selecione **Home Assistant**, informe a URL pública com `https://` e toque em **Autenticar com Home Assistant**.
6. Autorize o acesso na página oficial do Home Assistant e volte ao app. O envio começa automaticamente.
7. Na dashboard do Home Assistant, adicione um cartão **Mapa** e escolha a entidade `device_tracker` da Geely.

A integração apresenta apenas um conjunto enxuto de sensores para automações. O app pode continuar enviando o quadro JSON completo para MQTT ou webhook, incluindo coordenadas GPS quando a permissão está ativa.
