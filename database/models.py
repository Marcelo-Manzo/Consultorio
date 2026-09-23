from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha_hash = Column(String)


class Paciente(Base):
    __tablename__ = "Pacientes"

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    telefone = Column(String)
    cpf = Column(String)

    consultas = relationship("Consulta", back_populates="paciente")


class Consulta(Base):
    __tablename__ = "Consultas"

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("Pacientes.id"))
    data = Column(DateTime)
    tratamento = Column(String)
    valor = Column(Float)
    metodo_pagamento = Column(String)
    compareceu = Column(Integer, default=0)
    pago = Column(Boolean, default=False)

    paciente = relationship("Paciente", back_populates="consultas")


class Orcamento(Base):
    __tablename__ = "Orcamentos"

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    consulta_id = Column(Integer, ForeignKey("Consultas.id"))
    paciente_id = Column(Integer, ForeignKey("Pacientes.id"))
    valor = Column(Float)
    forma_pagamento = Column(String)
    status = Column(Integer, default=0)
    data_criacao = Column(DateTime)


class Tratamento(Base):
    __tablename__ = "Tratamentos"

    usuario_id = Column(Integer, ForeignKey("Usuarios.id"))
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    valor = Column(Float)
