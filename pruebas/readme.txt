Instrucciones de uso:
Para el diagnóstico completo:

    Guarda el código como diagnostico_fijo.py

    Ejecuta: python diagnostico_fijo.py

    Revisa los archivos generados:

        diagnostico_YYYYMMDD_HHMMSS.log - Log completo

        reporte_diagnostico.json - Reporte en JSON

        wsdl_dump.xml - Respuesta WSDL del servidor

        respuesta_wtsp_loginout.xml - Respuesta SOAP de login

Para la prueba rápida:

    Guarda como prueba_rapida.py

    Ejecuta: python prueba_rapida.py

Qué hará el diagnóstico:

    ✅ Resolverá el DNS del servidor

    ✅ Probará si el puerto 80 está abierto

    ✅ Hará un HTTP GET para ver si el servicio web responde

    ✅ Enviará un request SOAP de login con tus credenciales

    ✅ Enviará un request SOAP de WTSP_CHKROUTE

    ✅ Probará URLs alternativas

    ✅ Verificará la configuración de tu sistema

    ✅ Generará un reporte completo con recomendaciones

####################################################################################################################################

Instrucciones RÁPIDAS:

    1. Guarda el primer archivo como descubrir_url.py

    2. Ejecuta el script:
        python descubrir_url.py

    3. Buscará automáticamente entre más de 100 URLs posibles

    4. Si encuentra el webservice, te mostrará:

        * La URL correcta

        * Cómo usarla en tu código

        * La guardará en url_correcta.txt