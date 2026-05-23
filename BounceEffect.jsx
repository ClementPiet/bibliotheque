// ============================================================
// BOUNCE EFFECT — After Effects Script
// Applique un effet de rebond sur l'Échelle et la Rotation
// Usage : File > Scripts > Run Script File...
// ============================================================

(function () {

    var comp = app.project.activeItem;
    if (!comp || !(comp instanceof CompItem)) {
        alert("Veuillez ouvrir une composition.");
        return;
    }

    var layers = comp.selectedLayers;
    if (layers.length === 0) {
        alert("Sélectionnez au moins un calque.");
        return;
    }

    // ── Interface ──────────────────────────────────────────
    var dlg = new Window("dialog", "Effet de Rebond");
    dlg.alignChildren = ["fill", "top"];
    dlg.spacing = 10;
    dlg.margins = 16;

    var pnl = dlg.add("panel", undefined, "Paramètres");
    pnl.alignChildren = ["fill", "top"];
    pnl.margins = [14, 20, 14, 14];
    pnl.spacing = 8;

    function addRow(parent, label, defaultVal) {
        var row = parent.add("group");
        row.alignment = "fill";
        row.alignChildren = ["fill", "center"];
        row.add("statictext", undefined, label).alignment = ["fill", "center"];
        var fld = row.add("edittext", undefined, String(defaultVal));
        fld.preferredSize.width = 65;
        fld.alignment = ["right", "center"];
        return fld;
    }

    var durationFld  = addRow(pnl, "Durée de l'animation (sec) :",  "1.5");
    var overshootFld = addRow(pnl, "Dépassement échelle (%) :",      "25");
    var rotAmpFld    = addRow(pnl, "Amplitude rotation (°) :",       "15");
    var bouncesFld   = addRow(pnl, "Nombre de rebonds :",             "3");
    var decayFld     = addRow(pnl, "Amortissement (1=doux / 10=vif):", "5");

    var cbPnl = dlg.add("panel", undefined, "Appliquer sur");
    cbPnl.orientation = "row";
    cbPnl.margins = [14, 20, 14, 14];
    var cbScale = cbPnl.add("checkbox", undefined, "Échelle");
    cbScale.value = true;
    var cbRot = cbPnl.add("checkbox", undefined, "Rotation");
    cbRot.value = true;

    var btnGrp = dlg.add("group");
    btnGrp.alignment = "center";
    btnGrp.spacing = 10;
    var applyBtn  = btnGrp.add("button", undefined, "Appliquer", { name: "ok" });
    var cancelBtn = btnGrp.add("button", undefined, "Annuler",   { name: "cancel" });
    applyBtn.preferredSize.width  = 100;
    cancelBtn.preferredSize.width = 100;

    cancelBtn.onClick = function () { dlg.close(); };

    applyBtn.onClick = function () {
        var p = {
            duration:    Math.max(0.1, parseFloat(durationFld.text)  || 1.5),
            overshoot:   parseFloat(overshootFld.text) || 25,
            rotAmp:      parseFloat(rotAmpFld.text)    || 15,
            numBounces:  Math.max(1, parseInt(bouncesFld.text)   || 3),
            decay:       Math.max(0.5, parseFloat(decayFld.text) || 5),
            applyScale:  cbScale.value,
            applyRot:    cbRot.value
        };
        dlg.close();
        runEffect(layers, p);
    };

    dlg.show();

})();


// ── Application de l'effet ────────────────────────────────
function runEffect(layers, p) {
    app.beginUndoGroup("Bounce Effect");
    try {
        for (var i = 0; i < layers.length; i++) {
            applyBounce(layers[i], p);
        }
        alert("Rebond appliqué sur " + layers.length + " calque(s) !");
    } catch (err) {
        alert("Erreur : " + err.message);
    }
    app.endUndoGroup();
}


function applyBounce(layer, p) {

    var dur   = p.duration;
    var over  = (p.overshoot / 100).toFixed(6);   // ex : 0.25
    var amp   = p.rotAmp.toFixed(4);
    var decay = p.decay.toFixed(4);
    // Fréquence : numBounces oscillations complètes sur `dur` secondes
    var freq  = (p.numBounces * 2 * Math.PI / dur).toFixed(8);

    // ── Échelle ──────────────────────────────────────────
    // Formule : 100 * (1 + over * sin(freq*t + π/2) * e^(-decay*t))
    //   t=0  → sin(π/2)=1  → 100*(1+over) = apparition brusque à ~125 %
    //   t→∞  → 0           → stabilisation à 100 %
    if (p.applyScale) {
        var sp = layer.transform.scale;
        sp.expression = "";
        while (sp.numKeys > 0) sp.removeKey(1);

        sp.expression = [
            "var t0    = inPoint;",
            "var over  = " + over  + ";",
            "var decay = " + decay + ";",
            "var freq  = " + freq  + ";",
            "",
            "if (time < t0) {",
            "  value.length > 2 ? [0,0,0] : [0,0];",
            "} else {",
            "  var t  = time - t0;",
            "  var sv = 100 * (1 + over * Math.sin(freq * t + Math.PI / 2) * Math.exp(-decay * t));",
            "  sv = Math.max(0, sv);",
            "  value.length > 2 ? [sv, sv, sv] : [sv, sv];",
            "}"
        ].join("\n");
    }

    // ── Rotation ─────────────────────────────────────────
    // Formule : amp * cos(freq*t) * e^(-decay*t)
    //   t=0  → cos(0)=1  → rotation initiale = amp  (ex : 15°)
    //   t→∞  → 0         → stabilisation à 0°
    if (p.applyRot) {
        var rp = layer.transform.rotation;
        rp.expression = "";
        while (rp.numKeys > 0) rp.removeKey(1);

        rp.expression = [
            "var t0    = inPoint;",
            "var amp   = " + amp   + ";",
            "var decay = " + decay + ";",
            "var freq  = " + freq  + ";",
            "",
            "if (time < t0) {",
            "  0;",
            "} else {",
            "  var t = time - t0;",
            "  amp * Math.cos(freq * t) * Math.exp(-decay * t);",
            "}"
        ].join("\n");
    }
}
