<?php include "includes/head.php" ?>
    <title>The Science's on the Table - Contato</title>
</head>

<!-- corpo do site -- >
<body>
    <!-- menu superior (fixado) -->
<?php include "includes/menu.php"  ?>
    <!-- fim do menu superior (fixado) -->



    <!-- inicio div de chamada do site -->
<?php include "includes/chamada.php"  ?>
    <!-- fim div de chamada do site -->


    <!-- (new) inicio div de corpo do site -->
    <div class="jumbotron-fluid">
        <div class="container">
            <!-- form de contato -->
            <div class="form-area">
                <form role="form">
                    <h2 class="h1-responsive font-weight-bold text-center my-5">Contato</h2>
                    <!-- campo nome-->
                    <div class="form-group">
                        <input type="text" class="form-control" id="nome" name="nome" placeholder="Nome">
                    </div>
                    <!-- campo email-->
                    <div class="form-group">
                        <input type="text" class="form-control" id="email" name="email" placeholder="E-mail">
                    </div>
                    <!-- campo mensagem -->
                    <div class="form-group">
                        <textarea class="form-control" type="textarea" id="msg" placeholder="Mensagem" maxlength="500" rows="7"></textarea>
                        <span class="help-block">
                            <p id="charsrestantes" class="help-block">Você atingiu o limite</p>
                        </span>
                    </div>
                    <!-- botão de envio -->
                    <button type="button" id="enviar" name="enviar" class="btn btn-success pull-right">Enviar</button>
                </form>

            </div>
        </div>
    </div>
    <!-- (new) fim div de corpo do site -->


    <!-- rodapé do site -->
<?php include "includes/rodape.php" ?>

<!-- script de caracteres restantes -->
<script type="text/javascript" src="js/caracteres-restantes.js"></script>