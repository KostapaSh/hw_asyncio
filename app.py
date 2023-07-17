import aiohttp
import asyncio
import requests
from more_itertools import chunked
from models import Person, Session, Base, engine
import warnings


def get_all_id() -> int:
    lasr_id = requests.get('https://swapi.dev/api/people/').json()['count']
    print(f'Персонажей в БД ресурса - {lasr_id}')
    return lasr_id

async def get_person_for_bd(session: aiohttp.client.ClientSession, range_person_id: int):
    warnings.filterwarnings('ignore')


    persons_list = (get_person_from_url(session, person_id) for person_id in range(1, range_person_id))

    person_list_chunked = chunked(persons_list, 10)
    for person_list_chunk in person_list_chunked:
        persons = await asyncio.gather(*person_list_chunk)
        asyncio.create_task(add_to_bd(persons))

async def get_person_from_url(session: aiohttp.client.ClientSession, person_id: int):
    respons = await session.get(f'https://swapi.dev/api/people/{person_id}', ssl=False)
    json_data_url = await respons.json()
    json_data_url['person_id'] = person_id
    json_data_with_id = json_data_url
    #print(json_data_with_id)
    return json_data_with_id

async def add_to_bd(persons):
    async with Session() as session:
        for person in persons:
            try:
                add_db = Person(
                    id = int(person['person_id']),
                    name = str(person['name']),
                    birth_year = str(person['birth_year']),
                    eye_color = str(person['eye_color']),
                    films = str(person['films']),
                    gender = str(person['gender']),
                    hair_color = str(person['hair_color']),
                    height = str(person['height']),
                    homeworld = str(person['homeworld']),
                    mass = str(person['mass']),
                    skin_color = str(person['skin_color']),
                    species = str(person['species']),
                    starships = str(person['starships']),
                    vehicles = str(person['vehicles']),
                )
                session.add(add_db)
                await session.commit()
            except KeyError:
                print(person)



async def main():
    id = get_all_id()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    async with aiohttp.client.ClientSession() as session:
        await get_person_for_bd(session, id)
        await session.close()

    tasks = asyncio.all_tasks() - {
        asyncio.current_task(),
    }
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())