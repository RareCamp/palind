
async function sha256(message) {
  // encode as UTF-8
  const msgBuffer = new TextEncoder().encode(message);

  // hash the message
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);

  // convert ArrayBuffer to Array
  const hashArray = Array.from(new Uint8Array(hashBuffer));

  // convert bytes to hex string                  
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}


function sanitize(s) {
  s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  s = s.replace(/[^a-zA-Z]/gi, "");
  s = s.toLowerCase();
  return s;
}

function qgrams(s, q = 2) {
  if (s.length <= q) {
    return [s];
  }
  var result = [];
  for (var i = 0; i < s.length - q + 1; i++) {
    result.push(s.slice(i, i + q));
  }
  return result;
}

function bloomFilter(chunks, length = 1024, eps = 2) {
  let bf = new Array(length).fill(false);
  chunks.forEach(async (chunk) => {
    for (
      var i = 0;
      i < Math.round((Math.log(2) * length) / chunks.length);
      i++
    ) {
      const hash = await sha256(chunk + "#" + i);
      let index = parseInt(hash.slice(0, 10), 16) % length;
      bf[index] = true;
    }
  });
  for (var i = 0; i < length; i++) {
    if (Math.random() < 1 / (1 + Math.exp(eps))) {
      bf[i] = !bf[i];
    }
  }
  return bf;
}

async function curesDevTokenize(s) {
  return bloomFilter(qgrams(sanitize(s)));
}
