document.getElementById('guardarArchivo').addEventListener('click', () => {
  let texto = document.getElementById('textoArchivo').value;


  let blob = new Blob([texto], { type: 'text/plain' });

  let link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'archivo.txt';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});
