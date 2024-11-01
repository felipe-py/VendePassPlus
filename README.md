<h3 align="center">VendePass</h3>

<div align="justify"> 
<div id="sobre-o-projeto"> 
<h2> Descrição do Projeto</h2>

Tomando como base o Projeto VendePass, que cria um sistema de relacionamento cliente/servidor para a compara de passagens aéreas. Desenvolveremos neste projeto um sistema que também tem como objeto a venda de passagens aéreas a baixo custo, entretanto desta vez teremos um compartilhamento destas funcionalidades para mais servidores.

Nesta aplicação, um cliente que deseja realizar a compra de uma passagem terá a sua disposição três empresas aéreas. Cada empresa aérea possuirá seu próprio servidor, porém, o cliente tem a opção de ao estar realizando a compra em um servidor A, ter acesso as passagens de B e C.

As funcionalidades devem estar em funcionamneto sem a necessidade de um servidor central para gerenciamento dos dados e operações das três empresas. Isso tira a dependência total que teríamos caso o servidor central estivesse em operação.

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
        <li><a href="protocolo"> Protocolo de Comunicação </a></li>
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

O diagrama que apresenta a arquitetura geral da solução pode ser visualizado na Figura 1, nele podem ser observadas a relaçao entre cliente, servidores e base de dados da aplicação.

<p align="center">
  <img src="docs/diagrama_arquitetura.png" width = "500" />
</p>
<p align="center"><strong> Figura 1. Arquitetura Geral do Sistema </strong></p>

O cliente inicialmente terá a opção de se conectar a qualquer um dos três servidores, o servidor ao qual ele se conectar se tornará de certa maneira o servidor central para ele.

Este servidor em que foi feita a conexão, poderá realizar qualquer tipo de consulta ou ação que envolva os outros dois servidores. Esta dinêmica desenvolve um ambiente totalmente compartilhado, em que não se faz necessário a necessidade e dependência de utilizarmos um servidor central.

Cada servidor terá a sua própria base de dados de forma independente, englobando as informações relacionadas as suas rotas e passagens que foram vendidas. Além disso os dados que envolvem a relação de clientes cadastrados é comum a todos os servidores.

</div>
</div>

<div id="protocolo">
<h2> Protocolo de Comunicação </h2>
<div align="justify">



</div>
</div>

<div id="roteamento">
<h2> Roteamento </h2>
<div align="justify">



</div>
</div>

<div id="concorrencia">
<h2> Concorrência Distribuída </h2>
<div align="justify">



</div>
</div>

<div id="confiabilidade">
<h2> Confiabilidade da Solução </h2>
<div align="justify">



</div>
</div>

<div id="docker">
<h2> Utilização do Docker </h2>
<div align="justify">



</div>
</div>

<div id="conclusao">
<h2> Conclusão </h2>
<div align="justify">



</div>
</div>

<div id="referencias">  
<h2> Referências</h2>
<div align="justify">



</div>
</div>
