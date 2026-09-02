from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Paciente(Base):
    __tablename__ = "Pacientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    telefone = Column(String)
    cpf = Column(String)

    consultas = relationship("Consulta", back_populates="paciente")


class Consulta(Base):
    __tablename__ = "Consultas"

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

    id = Column(Integer, primary_key=True)
    consulta_id = Column(Integer)
    paciente_id = Column(Integer)
    valor = Column(Float)
    forma_pagamento = Column(String)
    status = Column(Integer, default=0)
    data_criacao = Column(DateTime)


class Tratamento(Base):
    __tablename__ = "Tratamentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    valor = Column(Float)
