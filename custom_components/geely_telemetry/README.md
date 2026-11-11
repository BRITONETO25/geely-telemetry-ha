# Geely Telemetry para Home Assistant

Integração customizada que mostra sensores comuns do veículo e uma entidade `device_tracker` para GPS. Recebe quadros do app pela internet ou lê a central na rede local.

## Instalação

1. Copie a pasta `geely_telemetry` para `config/custom_components/` no Home Assistant.
2. Reinicie o Home Assistant e adicione a integração **Geely Telemetry**.
3. Para receber pela internet, escolha **App do carro pela internet**. Para uso apenas local, escolha **Rede local** e informe o endereço e a porta da central.
4. No app do carro, permita o acesso à localização quando solicitado.
5. No app, abra **Destino**, selecione **Home Assistant**, informe a URL pública com `https://` e toque em **Autenticar com Home Assistant**.
6. Entre na página oficial do Home Assistant, aprove o acesso e volte ao app. O envio começa automaticamente.
7. Na dashboard do Home Assistant, adicione um cartão **Mapa** e escolha a entidade `device_tracker` da Geely.

A integração apresenta somente sensores comuns para automações. O app continua enviando o quadro JSON completo para outros destinos como MQTT e webhook, incluindo coordenadas GPS quando a permissão está ativa.
