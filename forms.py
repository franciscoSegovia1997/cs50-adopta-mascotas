from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class TipoMascotaForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre no puede estar vacio")],
    )
    descripcion = TextAreaField("Descripcion")
    submit = SubmitField("Guardar")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        nombre = (self.nombre.data or "").strip().lower()
        descripcion = (self.descripcion.data or "").strip().lower()
        if nombre and descripcion and nombre == descripcion:
            self.descripcion.errors.append(
                "El nombre y la descripcion no deben ser iguales"
            )
            return False
        return True
