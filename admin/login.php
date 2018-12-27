<?php include "includes/head.php" ?>
    <title>The Science's on the Table - Login</title>
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
                    <h2 class="h1-responsive font-weight-bold text-center my-5">Login</h2>
                    <!-- campo email -->
                    <div class="form-group">
                        <input type="text" class="form-control" id="email" name="email" placeholder="E-mail" required>
                    </div>
                    <!-- campo senha -->
                    <div class="form-group">
                        <input type="password" class="form-control" id="senha" name="senha" placeholder="Senha" required>
                    </div>
                    <!-- botão de login -->
                    <button type="button" id="enviar" name="enviar" class="btn btn-success pull-right">Login</button>
                </form>

            </div>
        </div>
    </div>
    <!-- (new) fim div de corpo do site -->


    <!-- rodapé do site -->
<?php include "../includes/rodape.php" ?>