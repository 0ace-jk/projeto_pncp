# projeto_pncp
Esse projeto tem como objetivo solucionar um problema... 

\

*Mas que problema é esse ?*

Para uma certa atividade, era necessario a coleta de dados de licitações do governo para analisar preços de itens, etc... Mas essa atividade era feita de forma totalmente manual, dessa forma identifiquei a possibilidade de automatizar essa coleta utilizando python.

Utilizando a biblioteca requests e a API do portal do PNCP, foi possível buscar por todos os contratos abertos em um período determinado...

\

*Mas ainda havia um problema*

Essa API do PNCP entrega apenas as contratações, e não os itens que contém em cada contrato, tornando a necessário a utilização de outras bibliotecas como o Selenium, para fazer o Web Scrapping de site por site desses contratos do PNCP e extrair todos os itens que contém em cada contrato.

\

*E quais foram os resultados ?*

Esse codigo consegue otimizar muito o tempo dessa coleta dos dados, trazendo o esforço para as análises das informações, fazendo com que carregue, em cerca de meia hora, 1000 contratações e até 5000 itens.

utilizando a biblioteca pandas para fazer todo o DataFrame e em seguida, conversão para CSV ou EXCEL.

*Como bonus*

Foi implementado também no final do codigo, com o uso de bibliotecas do SMTPLIB e de envio de emails, foi possivel enviar todos esses dados por e-mail de forma automatizada.
