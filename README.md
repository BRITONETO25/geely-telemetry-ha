# Geely Telemetry para Home Assistant

App de telemetria para a central do **Geely EX2 vendido no Brasil**, junto com a integração customizada para Home Assistant. A integração oferece sensores selecionados e uma entidade GPS (`device_tracker`). O app pode publicar quadros JSON completos por MQTT ou webhook.

> **Compatibilidade:** o desenvolvimento e a validação foram feitos para o Geely EX2 brasileiro. O protocolo e os sinais podem variar conforme o país, ano, versão de software ou modelo. Portanto, pode funcionar ou não em versões internacionais do EX2 e em outros veículos Geely; esses casos ainda não foram validados.

## Arquivos

- APK de depuração: [`app/Geely-Telemetry-debug.apk`](app/Geely-Telemetry-debug.apk). Por ser uma compilação de depuração, use para avaliação e testes.
- Integração Home Assistant: `custom_components/geely_telemetry/`.

## Recursos

- Velocidade, marcha, bateria de tração, autonomia, dados da viagem, carregamento e conexão.
- Entidade `device_tracker` para mostrar a localização do carro em um cartão de mapa.
- Recepção de dados do app pela internet com autorização OAuth do Home Assistant ou leitura local pela rede.
- O app pode publicar o quadro VHAL legível completo em MQTT ou webhook.

## Instalar a integração pelo HACS

1. No HACS, abra **Integrações** e escolha **Repositórios personalizados** no menu. Enquanto a solicitação de entrada no catálogo padrão estiver pendente, adicione este repositório manualmente.
2. Adicione `https://github.com/BRITONETO25/geely-telemetry-ha` com a categoria **Integration**.
3. Baixe **Geely Telemetry** e reinicie o Home Assistant.
4. Adicione a integração. Selecione **App do carro pela internet** para envio remoto ou **Rede local** para leitura na LAN.
5. No app instalado na central, selecione **Home Assistant**, informe a URL pública `https://` e toque em **Autenticar**.
6. Autorize o acesso na página do Home Assistant e retorne ao app.
7. Para o mapa, adicione um cartão **Mapa** à dashboard e selecione a entidade `device_tracker` da Geely.

## Instalar o app na central

Baixe o APK acima e instale-o na central do veículo. O APK neste repositório é uma compilação de depuração, não uma versão de produção assinada.

## Privacidade e limitações

O app precisa da permissão de localização do Android para enviar coordenadas GPS. A telemetria vai apenas para os destinos habilitados no app. Os tokens OAuth são armazenados de forma criptografada na central. O app lê sinais do veículo e a localização, sem enviar comandos de controle ao carro.

A integração expõe um conjunto enxuto de sensores comuns. O hodômetro não estava disponível no snapshot VHAL do veículo usado nos testes.

## Suporte

Abra uma issue neste repositório para reportar problemas ou sugerir recursos.

## Licença

MIT.
