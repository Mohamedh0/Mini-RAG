from .BaseDataModel import BaseDataModel
from .db_schemes.minirag.schemes import Project
from sqlalchemy.future import select
from sqlalchemy import func


class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        # db_client is a sessionmaker: call it to get a session

    @classmethod
    async def create_instance(cls, db_client: object):
        return cls(db_client)

    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():   # commits automatically on exit
                session.add(project)
            await session.refresh(project)
        return project

    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            result = await session.execute(
                select(Project).where(Project.project_id == project_id)
            )
            project = result.scalar_one_or_none()

        if project is None:
            project = await self.create_project(Project(project_id=project_id))

        return project

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        async with self.db_client() as session:
            total_documents = (
                await session.execute(select(func.count(Project.project_id)))
            ).scalar_one()

            total_pages = (total_documents + page_size - 1) // page_size

            result = await session.execute(
                select(Project).offset((page - 1) * page_size).limit(page_size)
            )
            projects = result.scalars().all()

        return projects, total_pages
