from sqlmodel import Session


class UnitOfWork:
    # el UoW es el único lugar donde hacemos commit y rollback
    # los repositorios solo hacen flush para obtener IDs sin confirmar

    def __init__(self, session: Session) -> None:
        self._session = session

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # si salimos del bloque sin excepciones confirmamos todo
        # si hubo alguna excepción deshacemos todo
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
