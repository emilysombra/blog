<?php include "includes/head.php" ?>
    <title>The Science's on the Table - Novo Post</title>
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
            <!-- form de post novo -->
            <div class="form-area">
                <form role="form">
                    <h2 class="h1-responsive font-weight-bold text-center my-5">Novo Post</h2>
                    <!-- campo título-->
                    <div class="form-group">
                        <label for="titulo">Título do Post:</label>
                        <input type="text" class="form-control" id="titulo" name="titulo" placeholder="Título" required>
                    </div>
                    <!-- campo imagem-->
                    <div class="form-group">
                        <label for="img">Imagem:</label>
                        <input type="file" class="form-control" id="img" name="img" required>
                    </div>
                    <!-- campo post -->
                    <div class="form-group">
                        <textarea class="form-control" type="textarea" id="texto" placeholder="Conteúdo do Post" rows="7"></textarea>
                        <span class="help-block">
                    </div>
                    <!-- botão de envio -->
                    <button type="button" id="enviar" name="enviar" class="btn btn-success pull-right">Enviar</button>
                </form>

            </div>
        </div>
    </div>
    <!-- (new) fim div de corpo do site -->


    <!-- rodapé do site -->
<?php include "../includes/rodape.php" ?>