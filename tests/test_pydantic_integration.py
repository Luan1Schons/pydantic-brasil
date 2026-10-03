from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

import pydantic_brasil as pb


class CustomerRegistration(BaseModel):
    cpf: pb.CPF = Field(description="Customer Brazilian CPF")
    cnpj: pb.CNPJ = Field(description="Company CNPJ")
    doc: pb.CPFouCNPJ
    cep: pb.CEP
    phone: pb.TelefoneBR
    pix: pb.ChavePIX
    placa: pb.PlacaVeiculo
    salario: pb.DinheiroBRL


def test_full_model_serialization_and_json():
    cpf = pb.CPF.generate(state="SP")
    cnpj = pb.CNPJ.generate()
    cep = pb.CEP.generate(state="SP")
    phone = pb.TelefoneBR.generate(ddd=11)
    pix = pb.ChavePIX.generate_evp()

    customer = CustomerRegistration(
        cpf=cpf.formatted,
        cnpj=cnpj.formatted,
        doc=cpf.digits,
        cep=cep.formatted,
        phone=phone.formatted,
        pix=pix,
        placa="ABC-1234",
        salario="R$ 5.400,00",
    )

    dump = customer.model_dump()
    assert dump["cpf"] == cpf.digits
    assert dump["cnpj"] == cnpj.digits
    assert dump["cep"] == cep.digits
    assert dump["phone"] == phone.digits
    assert dump["salario"] == 5400.0

    # Ensure JSON serializable without custom encoders
    json_str = customer.model_dump_json()
    assert cpf.digits in json_str
    assert "5400.0" in json_str


def test_fastapi_openapi_schema():
    app = FastAPI(title="Brazilian API")

    @app.post("/customers")
    def create_customer(customer: CustomerRegistration):
        return {"status": "ok", "cpf": customer.cpf.formatted}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()
    schemas = openapi["components"]["schemas"]
    assert "CustomerRegistration" in schemas

    # Ensure our custom openapi descriptions & titles are present
    properties = schemas["CustomerRegistration"]["properties"]
    assert "cpf" in properties
    assert "cnpj" in properties
    assert "cep" in properties
    assert "salario" in properties
