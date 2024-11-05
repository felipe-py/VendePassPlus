<h3 align="center">VendePass</h3>

<div align="justify"> 
<div id="sobre-o-projeto"> 
<h2> Descrição do Projeto</h2>

Tomando como base o Projeto VendePass, que cria um sistema de relacionamento cliente/servidor para a compara de passagens aéreas. Desenvolveremos neste projeto um sistema que também tem como objeto a venda de passagens aéreas a baixo custo, entretanto desta vez teremos um compartilhamento destas funcionalidades para mais servidores.

Nesta aplicação, um cliente que deseja realizar a compra de uma passagem terá a sua disposição três empresas aéreas. Cada empresa aérea possuirá seu próprio servidor, porém, o cliente tem a opção de ao estar realizando a compra em um servidor A, ter acesso as passagens de B e C.

As funcionalidades devem estar em funcionamneto sem a necessidade de um servidor central para gerenciamento dos dados e operações das três empresas. Isso retira a dependência total que teríamos caso o servidor central estivesse em operação.

Para mais informações sobre o projeto VendePass, acesse: <li><a href="https://github.com/felipe-py/VendePass">VendePass Repositório</a></li>

</div>
</div>

<h2> Autores <br></h2>
<uL>
  <li><a href="https://github.com/felipe-py">Felipe Silva</a></li>
  <li><a href="https://github.com/Lucas-L-Rodrigues">Lucas Lima</a></li>
</ul>


<h1 align="center"> Sumário </h1>
<div id="sumario">
	<ul>
        <li><a href="#arquitetura"> Arquitetura da Solução </a></li>
        <li><a href="#protocolo"> Protocolo de Comunicação </a></li>
        <li><a href="#roteamento"> Roteamento </a></li>
        <li><a href="#concorrencia"> Concorrência Distribuída</a></li>
        <li><a href="#confiabilidade"> Confiabilidade da Solução </a></li>
        <li><a href="#docker"> Utilização do Docker </a></li>
        <li><a href="#conclusao"> Conclusão </a></li>
        <li><a href="#referencias"> Referências </a></li>
	</ul>	
</div>

</div id="arquitetura">
<h2> Arquitetura da Solução </h2>
<div align="justify">

O diagrama que apresenta a arquitetura geral da solução pode ser visualizado na Figura 1, nele podem ser observadas a relação entre cliente, servidores e base de dados da aplicação.

<p align="center">
  <img src="docs/diagrama_arquitetura.png" width = "500" />
</p>
<p align="center"><strong> Figura 1. Arquitetura Geral do Sistema </strong></p>

O cliente inicialmente terá a opção de se conectar a qualquer um dos três servidores, o servidor ao qual ele se conectar se tornará de certa maneira o servidor central para ele neste momento inicial das operações..

A partir do servidor conectado ele poderá realizar operações neste servidor, ou, ter acesso aos servidores parceiros e realizar sua compra. Importante salientar que ele só poderá realizar a conexão em servidores que estão ativos.

Cada servidor terá a sua própria base de dados de forma independente, englobando as informações relacionadas as suas rotas e passagens que foram vendidas. Além disso os dados que envolvem a relação de clientes cadastrados é comum a todos os servidores.

<h3> Conexão Cliente/Servidor </h3>

De maneira geral, o cliente realizará as requisições e o servidor se torna responsável por processar estas requisições. A comunicação entre os dois agentes é feita através do protocolo http, que permite o envio dos dados de forma estrutura entre eles.

Para o controle e identificação destas requisições, foi utilizada a APIRest com a biblioteca Flask do Python. As requisições são construídas com os dados necessários para a sua execução e o servidor responde a partir do resultado deste processamento.

Verificações são feitas para que o cliente acesse as informações dos servidores que estão em atividade, evitando problemas durante as execuções das requisições.

<h3> Conexão entre servidores </h3>

A conexão entre servidores mantém a mesma lógica utilizada para a conexão entre cliente e servidor, isso ocorre por que o servidor principal ao qual o usuário escolhe inicialmente se torna de certa forma um cliente para os outros servidores.

Os recursos http são utilizados da mesma forma, assim como os requests utilizados pela API.

</div>

<div id="protocolo">
<h2> Protocolo de Comunicação </h2>
<div align="justify">



</div>
</div>

<div id="roteamento">
<h2> Roteamento </h2>
<div align="justify">

A distribuição dos trechos em um servidor é feita de maneira semelhante ao que foi desenvolvido para o projeto VendePass, os trechos estão definidos de forma pronta, ou seja, não se faz necessária a pesquisa cidade origem/destino. Serão exibidos ao usuário somente os trechos com assentos disponíveis para a compra, sendo está regra vigente para os três servidores.

<p align="center">
  <img src="docs/roteamento.png" width = "500" />
</p>
<p align="center"><strong> Figura 2. Roteamento de Rotas Entre Servidores </strong></p>

A relação de compartilhamento de rotas entre os servidores pode ser identificada na FIgura 2, nela podemos observar que os servidores podem se conectar entre si. Como cada servidor possui seu arquivo de armazenamento de trechos, devido ao compartilhamento entre servidores todos terão acesso aos trechos aéreos.

Devido a este compartilhamento, as funções de consulta e compra de trecho são comuns aos três servidores.

No diagrama apresentado na Figura 3 podemos realizar uma análise mais detalhada desta distribuição de trechos entre os servidores.

<p align="center">
  <img src="docs/distribuicao_trechos.png" width = "500" />
</p>
<p align="center"><strong> Figura 3. Compartilhamento de trechos entre servidores </strong></p>

</div>
</div>

<div id="concorrencia">
<h2> Concorrência Distribuída </h2>
<div align="justify">

Para o controle da concorrência distribuída foi utilizado o algoritmo de Ricart-Agrawala, um protocolo de controle utilizado para coordenar o acesso de processos a um recurso compartilhado de um sistema distribuído.

Neste caso, o algoritmo foi utilizado para coordenar o acesso as passagens durante momentos críticos, como a compra.

<h3> Funcionamento </h3>

O processo de controle é iniciado na requisição, quando um servidor inicia o processo de compra é instaurada uma mensagem de requisição para os outros servidores. O processo funciona de forma temporal, um timestamp e um indicador de solicitação do acesso.

O próximo passo é o tratamento dessa requisição, é feita a verificação da marca temporal para analisar se a requisição pode ser atendida de forma imediata ou se deve haver um retardamento da resposta. O processo que solicitou o recurso só terá acesso a ele quando houver permissão de todos os outros processos em execução.

Com a permissão concedida o processo poderá entrar na região crítica de operação para compra da passagem, com a passagem comprada ela não estará disponível para compra no banco de dados, finalizando o tratamento da requisição.

<h3> Vantagens e Limitações </h3>

O controle temporal feito pelo algoritmo garante o ordenamento das requisições, garantindo que não ocorra competição simultânea pelo mesmo recurso. Além disso, a troca de mensagens é feita de ponta a ponto, oq ue evita uma possível sobrecarga durante a comunicação.

Por se utilizar de características de controle temporais, em caso de ocorrência de muitas requisições simultâneas os processo terão que aguardar por diversas repostas, ocasionando atrasos. A falha em um dos servidores, pode de certa forma ocasionar em falhas devido a dependência da resposta dos outros servidores para a liberação das requisições.

</div>
</div>

<div id="confiabilidade">
<h2> Confiabilidade da Solução </h2>
<div align="justify">

Nos tópicos que envolvem a confiabilidade da solução, podemos analisar de maneira mais abrangente aqueles que envolvem os processos críticos de compra e cancelamento de uma passagem.

Em ambos os casos o tratamento para uma situação de queda de um servidor é semelhante, caso esta situação venha a ocorrer o processo que esta ocorrendo no momento é cancelado. Por tanto, o cliente não conseguirá finalizar o seu carrinho de compras se nele estiver contida a passagem de um servidor em falha. A situação será repetida em caso de cancelamento da compra de passagem.

Caso o servidor não esteja ativo no momento da escolha de acesso do cliente, um tratamento de exceção é feito para que o cliente acesse somente servidores ativos.

Em situações de estresse do sistema, podem ser observadas e esperadas algumas interferências. Isso ocorre principalmente em situações de acesso a região crítica, por ser utilizado um algoritmo de lógica temporal para controle da concorrência.

Situações de uso extremo, com muitos acessos simultâneos também podem ocasionar problemas nas atualizações dos arquivos json utilizados no banco de dados. Por ser utilizado um sistema mais simples de leitura e escrita em json, o alto fluxo pode hiperdimensionar os métodos de escrita e atualização dos dados.

</div>
</div>

<div id="conclusao">
<h2> Conclusão </h2>
<div align="justify">

Os tópicos principais que abrangem sistemas distribuídos e a concorrência distribuída foram corretamente abordados neste projeto, a distribuição de trechos entre mais de um servidor e a permissividade da compra em outros servidores é também aplicada no software.

A utilização do algoritmo de Ricart-Agrawala, apropriado para aplicações que possuem concorrência distribuída é aplicado de forma concreta em métodos que podem criar situações críticas de acesso a dados durante o processamento das requisições.Entretanto, devido a utilização deste algoritmo de lógica temporal, podem ser observados problemas de delay e atraso quando são processadas múltiplas requisições simultâneas.

Soluções podem ser aplicadas para contornar os problemas de latência causados pelo algoritmo, a utilização de buffering de mensagens pode ser usada para ordenamento correto das requisições e o uso de um timeout pode útil para evitar a perda de requisições quando multíplas delas são enviadas simultaneamente.

Outo ponto importante é a implementação de um 'rollback', para situações em que um servidor caia durante operações. Isso é importante para que o cliente não perca por exemplo, as compras no carrinho durante uma operação de compra em que o servidor tenha caído.

</div>
</div>

<div id="docker">
<h2> Utilização do Docker </h2>
<div align="justify">

[EM CONSTRUÇÃO]

</div>
</div>

<div id="referencias">  
<h2> Referências</h2>
<div align="justify">

Ricart–Agrawala Algorithm in Mutual Exclusion in Distributed System. Disponível em: <https://www.geeksforgeeks.org/ricart-agrawala-algorithm-in-mutual-exclusion-in-distributed-system/>.

KIDD, C. Distributed Systems Explained. Disponível em: <https://www.splunk.com/en_us/blog/learn/distributed-systems.html>.

</div>
</div>