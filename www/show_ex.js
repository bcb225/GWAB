function ex_show()
{
    form = document.getElementById("gwas_form");
    form.action = "toy_submit.php";
    
    gwas_row = document.getElementById("gwas_row");
    ex_gwas_row = document.getElementById("ex_gwas_row");
    gwas_row.hidden = true;
    ex_gwas_row.hidden = false;
    ex_gwas_text = document.getElementById("ex_gwas_input");
    ex_gwas_text.value = "CAD_lt0.01_input.txt";

    disease_row = document.getElementById("disease_row");
    ex_disease_row = document.getElementById("ex_disease_row");
    disease_row.hidden = true;
    ex_disease_row.hidden = false;

    ex_disease_text = document.getElementById("ex_disease_gene_set");
    ex_disease_text.value = "CAD.txt";
    ex_disease_text = document.getElementById("ex_disease_name");
    ex_disease_text.value = "Coronary Artery Disease (CAD)";
}
function true_show()
{
	form = document.getElementById("gwas_form");
    form.action = "submit.php";

    gwas_row = document.getElementById("gwas_row");
    ex_gwas_row = document.getElementById("ex_gwas_row");
    gwas_row.hidden = false;
    ex_gwas_row.hidden = true;

    disease_row = document.getElementById("disease_row");
    ex_disease_row = document.getElementById("ex_disease_row");
    disease_row.hidden = false;
    ex_disease_row.hidden = true;
}