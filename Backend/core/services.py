from sqlalchemy import select, update, delete
from database import session_factory
from models import *
from schemas import *
from typing import Optional, List
import numpy as np
import pandas as pd
import setuptools
import stumpy
from stumpy import config
from stumpy import core
import re
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.concurrency import run_in_threadpool


async def insert_time_series(file: UploadFile) -> List[int]:
    df = pd.read_csv(file.file)
    time_series = []
    is_timestamp = df.columns[0].lower().strip() == 'timestamp'
    if df.isnull().values.any() or df.shape[0] < 5 or is_timestamp and df.shape[1] < 2:  # Проверка на пропущенные значения и размерность
        return [False, "Неверное строение файла"]
    coord_names = df.columns
    if is_timestamp:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])  # Преобразование столбца в datetime
        coord_names = df.columns[1:]
    for title in coord_names:
        if (df[title]).dtypes == object:
            return [False, "Координаты должны быть типа float"]
        text = title
        if text.count('(') > 1 or text.count(')') > 1 or text.count('(') != text.count(')'):  # Проверяет что открывающаяся и закрывающаяся скобка одна
            return [False, "Неверное строение файла"]
        text = re.sub(r'\s+', ' ', text.strip())  # Убираются лишние пробелы и пробелы в начале и в конце строки
        temp = re.findall(r'([^(]+)\(((\s*\S+\s*)+)+\)', text)  # Возвращает список совпадений из обработанной строки
        if len(temp) == 0:
            temp = [text, None]
        else:
            temp = [temp[0][0].strip(), temp[0][1].strip()]

        time_series.append(TimeSeries(
            name=temp[0],
            stamp=df.iloc[:, 0] if is_timestamp else [],
            value=df[title],
            len=df.shape[0],
            description=temp[1]
        ))

    async with session_factory() as session:
        session.add_all(time_series)
        await session.commit()

    return [i.id for i in time_series]


async def get_time_series_to_display(project_id: int, user_id) -> List[DgTimeSeriesToDisplay]:
    async with session_factory() as session:
        query = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await session.execute(query)
        project = result.scalars().all()
        if not project:
            raise HTTPException(status_code=500, detail="Нет доступа!")

        query = select(TimeSeries).where(TimeSeries.project_id == project_id)
        result = await session.execute(query)
        time_series = result.scalars().all()

    return [DgTimeSeriesToDisplay.model_validate(item) for item in time_series]


async def get_time_series_for_data_grid(ts_ids: List[int]) -> List[DgTimeSeries]:
    async with session_factory() as session:
        query = select(TimeSeries).where(TimeSeries.id.in_(ts_ids))
        result = await session.execute(query)
        time_series = result.scalars().all()

    return [DgTimeSeries.model_validate(item) for item in time_series]


async def delete_time_series(ts_ids: List[int]) -> bool:
    async with session_factory() as session:
        query = delete(TimeSeries).where(TimeSeries.id.in_(ts_ids))
        await session.execute(query)
        await session.commit()

    return True


def сalculating_primitives(dict_primitives, time_series, matrix_profiles, motifs, discords, snippets, chains):
    if len(matrix_profiles) != 0:
        newlist = []
        for el in dict_primitives['MP']:
            if any(obj.ts_id == el.ts_id and obj.subseqLen == el.subseqLen for obj in matrix_profiles):
                continue
            newlist.append(el)

        dict_primitives['MP'] = newlist

    for el in dict_primitives['MP']:
        ts = next((ts for ts in time_series if ts.id == el.ts_id), [])
        config.STUMPY_EXCL_ZONE_DENOM = int(np.ceil(el.subseqLen / 2))
        mp = stumpy.stump(ts.value, m=el.subseqLen)
        matrix_profiles.append(MatrixProfile(
            ts_id=el.ts_id,
            nnDist=mp[:, 0],
            nnIdx=mp[:, 1],
            left_nnIdx=mp[:, 2],
            right_nnIdx=mp[:, 3],
            subseqLen=el.subseqLen,
        ))

    # Поиск мотивов
    for el in dict_primitives['M']:
        is_substitution = False
        motif = next((motif for motif in motifs if motif.ts_id == el.ts_id and motif.subseqLen == el.subseqLen), [])
        if motif:
            if motif.k >= el.topK:
                continue
            else:
                is_substitution = True

        ts = next((ts for ts in time_series if ts.id == el.ts_id), [])
        mp = [mp for mp in matrix_profiles if mp.ts_id == el.ts_id and mp.subseqLen == el.subseqLen]
        mp_df = pd.DataFrame(zip(mp[0].nnDist, mp[0].nnIdx)) if mp else []
        if not mp:
            config.STUMPY_EXCL_ZONE_DENOM = int(np.ceil(el.subseqLen / 2))
            mp = stumpy.stump(ts.value, m=el.subseqLen)
            mp_df = pd.DataFrame(mp)
            matrix_profiles.append(MatrixProfile(
                ts_id=el.ts_id,
                nnDist=mp[:, 0],
                nnIdx=mp[:, 1],
                left_nnIdx=mp[:, 2],
                right_nnIdx=mp[:, 3],
                subseqLen=el.subseqLen,
            ))

        mt = stumpy.motifs(ts.value, mp_df[0], max_matches=el.topK + 1)
        if not mt[0].any():
            continue

        mt_indexes = list(
            map(list, zip(mt[1][0][1:], mp_df.iloc[mt[1][0][1:], 1])))
        mt_indexes = np.array([sorted(el) for el in mt_indexes])

        if is_substitution:
            motif.indexes_left = mt_indexes[:, 0]
            motif.indexes_right = mt_indexes[:, 1]
            motif.nnDist = mt[0][0][1:]
            motif.k = len(mt[0][0][1:])
        else:
            motifs.append(Motif(
                ts_id=el.ts_id,
                indexes_left=mt_indexes[:, 0],
                indexes_right=mt_indexes[:, 1],
                nnDist=mt[0][0][1:],
                subseqLen=el.subseqLen,
                k=len(mt[0][0][1:]),
            ))

    # Поиск диссонансов
    for el in dict_primitives['D']:
        is_substitution = False
        discord = next((discord for discord in discords if discord.ts_id == el.ts_id and discord.subseqLen == el.subseqLen), [])
        if discord:
            if discord.k >= el.topK:
                continue
            else:
                is_substitution = True

        ts = next((ts for ts in time_series if ts.id == el.ts_id), [])
        mp = [mp for mp in matrix_profiles if mp.ts_id == el.ts_id and mp.subseqLen == el.subseqLen]
        mp_df = pd.DataFrame(zip(mp[0].nnDist, mp[0].nnIdx)) if mp else []
        if not mp:
            config.STUMPY_EXCL_ZONE_DENOM = int(np.ceil(el.subseqLen / 2))
            mp = stumpy.stump(ts.value, m=el.subseqLen)
            mp_df = pd.DataFrame(mp)
            matrix_profiles.append(MatrixProfile(
                ts_id=el.ts_id,
                nnDist=mp[:, 0],
                nnIdx=mp[:, 1],
                left_nnIdx=mp[:, 2],
                right_nnIdx=mp[:, 3],
                subseqLen=el.subseqLen,
            ))

        mp_df.sort_values(by=[0], ascending=False, inplace=True)
        ds = mp_df[abs(mp_df.index - mp_df.iloc[:, 1]) >= el.subseqLen]
        top_k_idxs = []
        for i in range(len(ds.index)):
            flag = True
            idx = ds.iloc[i].name
            for top_k_idx in top_k_idxs:
                if abs(top_k_idx - idx) < el.subseqLen:
                    flag = False
                    continue
            if flag:
                top_k_idxs.append(idx)
            if len(top_k_idxs) == el.topK:
                break

        if not top_k_idxs:
            continue

        ds = mp_df[mp_df.index.isin(top_k_idxs)][0]

        if is_substitution:
            discord.indexes = list(ds.index)
            discord.nnDist = list(ds)
            discord.k = len(top_k_idxs)
        else:
            discords.append(Discord(
                ts_id=el.ts_id,
                indexes=list(ds.index),
                nnDist=list(ds),
                subseqLen=el.subseqLen,
                k=len(top_k_idxs),
            ))

    # Поиск сниппетов
    for el in dict_primitives['S']:
        is_substitution = False
        snippet = next((snippet for snippet in snippets if snippet.ts_id == el.ts_id and snippet.subseqLen == el.subseqLen), [])
        if snippet:
            if snippet.k >= el.topK:
                continue
            else:
                is_substitution = True

        ts = next((ts for ts in time_series if ts.id == el.ts_id), [])

        sn = stumpy.snippets(ts.value, el.subseqLen, el.topK)
        sns = {'freq': [], 'idx': []}
        for i in range(len(sn[1])):
            if sns['idx'] and (sns['idx'][-1] == sn[1][i] or sn[1][i] in sns['idx']):
                break
            sns['freq'].append(sn[4][i])
            sns['idx'].append(sn[1][i])

        if not sns['idx']:
            continue

        if is_substitution:
            snippet.indexes = sns['idx']
            snippet.freq = sns['freq']
            snippet.k = len(sns['idx'])
        else:
            snippets.append(Snippet(
                ts_id=el.ts_id,
                indexes=sns['idx'],
                freq=sns['freq'],
                subseqLen=el.subseqLen,
                k=len(sns['idx']),
            ))

    # Поиск цепочек
    for el in dict_primitives['C']:
        is_substitution = False
        chain = next((chain for chain in chains if chain.ts_id == el.ts_id and chain.subseqLen == el.subseqLen), [])
        if chain:
            if chain.k >= el.topK:
                continue
            else:
                is_substitution = True

        ts = next((ts for ts in time_series if ts.id == el.ts_id), [])
        mp = [mp for mp in matrix_profiles if mp.ts_id == el.ts_id and mp.subseqLen == el.subseqLen]
        mp_df = pd.DataFrame(zip(mp[0].nnDist, mp[0].nnIdx, mp[0].left_nnIdx, mp[0].right_nnIdx)) if mp else []
        if not mp:
            config.STUMPY_EXCL_ZONE_DENOM = int(np.ceil(el.subseqLen / 2))
            mp = stumpy.stump(ts.value, m=el.subseqLen)
            mp_df = pd.DataFrame(mp)
            matrix_profiles.append(MatrixProfile(
                ts_id=el.ts_id,
                nnDist=mp[:, 0],
                nnIdx=mp[:, 1],
                left_nnIdx=mp[:, 2],
                right_nnIdx=mp[:, 3],
                subseqLen=el.subseqLen,
            ))

        all_chain_set, _ = stumpy.allc(mp_df[2], mp_df[3])
        ch = sorted(all_chain_set, key=len, reverse=True)[:el.topK]

        ch_num = [obj.size for obj in ch]
        ch_idx = np.concatenate(ch)
        if is_substitution:
            chain.indexes = list(ch_idx)
            chain.numElements = list(ch_num)
            chain.k = el.topK
        else:
            chains.append(Chain(
                ts_id=el.ts_id,
                indexes=list(ch_idx),
                numElements=list(ch_num),
                subseqLen=el.subseqLen,
                k=el.topK,
            ))

    return matrix_profiles, motifs, discords, snippets, chains


async def find_primitives(primitives: List[PrimitiveDTO]) -> int:
    primitive_names = {'D': "Диссонанс", 'M': "Мотив", 'S': "Сниппет", 'C': "Цепочка", 'MP': "Матричный профиль"}
    ts_ids = [el.ts_id for el in primitives]
    dict_primitives = {'D': [], 'M': [], 'S': [], 'C': [], 'MP': []}
    for primitive in primitives:
        if primitive.primitive_name == primitive_names['D']:
            dict_primitives['D'].append(primitive)
        if primitive.primitive_name == primitive_names['M']:
            dict_primitives['M'].append(primitive)
        if primitive.primitive_name == primitive_names['S']:
            dict_primitives['S'].append(primitive)
        if primitive.primitive_name == primitive_names['C']:
            dict_primitives['C'].append(primitive)
        if primitive.primitive_name == primitive_names['MP']:
            dict_primitives['MP'].append(primitive)

    async with session_factory() as session:
        query = select(TimeSeries).where(TimeSeries.id.in_(ts_ids))
        result = await session.execute(query)
        time_series = result.scalars().all()

        query = select(MatrixProfile).where(MatrixProfile.ts_id.in_(ts_ids))
        result = await session.execute(query)
        matrix_profiles = result.scalars().all()

        query = select(FoundPrimitive).where(FoundPrimitive.project_id == time_series[0].project_id)
        result = await session.execute(query)
        found_primitives = result.scalars().all()[0]

        discords = []
        motifs = []
        snippets = []
        chains = []
        if dict_primitives['D']:
            query = select(Discord).where(Discord.ts_id.in_([el.ts_id for el in dict_primitives['D']]),
                                          Discord.subseqLen.in_([el.subseqLen for el in dict_primitives['D']]))
            result = await session.execute(query)
            discords = result.scalars().all()
        if dict_primitives['M']:
            query = select(Motif).where(Motif.ts_id.in_([el.ts_id for el in dict_primitives['M']]),
                                          Motif.subseqLen.in_([el.subseqLen for el in dict_primitives['M']]))
            result = await session.execute(query)
            motifs = result.scalars().all()
        if dict_primitives['S']:
            query = select(Snippet).where(Snippet.ts_id.in_([el.ts_id for el in dict_primitives['S']]),
                                          Snippet.subseqLen.in_([el.subseqLen for el in dict_primitives['S']]))
            result = await session.execute(query)
            snippets = result.scalars().all()
        if dict_primitives['C']:
            query = select(Chain).where(Chain.ts_id.in_([el.ts_id for el in dict_primitives['C']]),
                                          Chain.subseqLen.in_([el.subseqLen for el in dict_primitives['C']]))
            result = await session.execute(query)
            chains = result.scalars().all()

    matrix_profiles, motifs, discords, snippets, chains = await run_in_threadpool(lambda: сalculating_primitives(dict_primitives, time_series, matrix_profiles, motifs, discords, snippets, chains))

    # Запись и обновление в бд
    async with session_factory() as session:
        session.add_all(matrix_profiles)
        if motifs:
            session.add_all(motifs)
        if discords:
            session.add_all(discords)
        if snippets:
            session.add_all(snippets)
        if chains:
            session.add_all(chains)
        await session.flush()
        found_primitives.matrix_pr_ids = list(set(found_primitives.matrix_pr_ids + [el.id for el in matrix_profiles]))
        found_primitives.motif_ids = list(set(found_primitives.motif_ids + [el.id for el in motifs]))
        found_primitives.discord_ids = list(set(found_primitives.discord_ids + [el.id for el in discords]))
        found_primitives.snippet_ids = list(set(found_primitives.snippet_ids + [el.id for el in snippets]))
        found_primitives.chain_ids = list(set(found_primitives.chain_ids + [el.id for el in chains]))
        session.add(found_primitives)
        await session.commit()

    return time_series[0].project_id


async def insert_project(item: InputProjectAndPrimitives, background_tasks: BackgroundTasks, user_id: int) -> bool:
    description = None
    if item.project.description and item.project.description.strip():
        description = re.sub(r'\s+', ' ', item.project.description.strip())

    project = Project(
        user_id=user_id,
        ts_ids=item.ts_ids if item.ts_ids else None,
        dim=len(item.ts_ids) if item.ts_ids else None,
        name=re.sub(r'\s+', ' ', item.project.project_name.strip()),
        description=description
    )

    async with session_factory() as session:
        session.add(project)
        await session.flush()
        session.add(FoundPrimitive(
            project_id=project.id,
            matrix_pr_ids=[],
            discord_ids=[],
            motif_ids=[],
            snippet_ids=[],
            chain_ids=[],
        ))
        query = update(TimeSeries).where(TimeSeries.id.in_(item.ts_ids)).values(project_id=project.id)
        await session.execute(query)
        await session.commit()

    if item.primitives:
        background_tasks.add_task(find_primitives, item.primitives)  # Запуск фоновой задачи
    return True


async def get_projects(user_id: int) -> List[DgProject]:
    async with session_factory() as session:
        query = select(Project).where(Project.user_id == user_id)
        result = await session.execute(query)
        projects = result.scalars().all()

    return [DgProject.model_validate(item) for item in projects]


async def delete_project(id: int) -> bool:
    async with session_factory() as session:
        query = delete(Project).where(Project.id == id)
        await session.execute(query)
        await session.commit()

    return True


async def update_project(id: int, project: ProjectDTO) -> bool:
    description = None
    if project.description and project.description.strip():
        description = re.sub(r'\s+', ' ', project.description.strip())

    async with session_factory() as session:
        query = update(Project).where(Project.id == id).values(name=re.sub(r'\s+', ' ', project.project_name.strip()), description=description)
        await session.execute(query)
        await session.commit()

    return True


async def get_data_for_project_editing(id: int) -> OutProjectAndTimeSeries:
    async with session_factory() as session:
        query = select(Project).where(Project.id == id)
        result = await session.execute(query)
        project = result.scalars().one()

        query = select(TimeSeries.name, TimeSeries.len, TimeSeries.description).where(TimeSeries.project_id == id)
        result = await session.execute(query)
        time_series = result.all()

    return OutProjectAndTimeSeries(
        project=ProjectDTO(project_name=project.name, description=project.description),
        time_series=[TimeSeriesDTO(ts_name=item[0], len=item[1], ts_description=item[2]) for item in time_series]
    )


async def save_time_series(id: int, file: UploadFile) -> List[TimeSeriesDTO]:
    async with session_factory() as session:
        query = select(TimeSeries.len, TimeSeries.stamp).where(TimeSeries.project_id == id)
        result = await session.execute(query)
        ts = result.all()

    df = pd.read_csv(file.file)
    time_series = []
    if ts and df.shape[0] != ts[0][0]:
        return [False, "Длина координат не совпадает"]
    is_timestamp = df.columns[0].lower().strip() == 'timestamp'
    if df.isnull().values.any() or df.shape[0] < 5 or is_timestamp and df.shape[1] < 2:  # Проверка на пропущенные значения и размерность
        return [False, "Неверное строение файла"]
    coord_names = df.columns
    if is_timestamp:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])  # Преобразование столбца в datetime
        coord_names = df.columns[1:]
    for title in coord_names:
        if (df[title]).dtypes == object:
            return [False, "Координаты должны быть типа float"]
        text = title
        if text.count('(') > 1 or text.count(')') > 1 or text.count('(') != text.count(
                ')'):  # Проверяет что открывающаяся и закрывающаяся скобка одна
            return [False, "Неверное строение файла"]
        text = re.sub(r'\s+', ' ', text.strip())  # Убираются лишние пробелы и пробелы в начале и в конце строки
        temp = re.findall(r'([^(]+)\(((\s*\S+\s*)+)+\)', text)  # Возвращает список совпадений из обработанной строки
        if len(temp) == 0:
            temp = [text, None]
        else:
            temp = [temp[0][0].strip(), temp[0][1].strip()]

        time_series.append(TimeSeries(
            name=temp[0],
            stamp=ts[0][1] if ts else (df.iloc[:, 0] if is_timestamp else []),
            value=df[title],
            len=df.shape[0],
            description=temp[1],
            project_id=id
        ))

    async with session_factory() as session:
        session.add_all(time_series)
        await session.commit()

    async with session_factory() as session:
        query = select(TimeSeries.name, TimeSeries.len, TimeSeries.description, TimeSeries.id).where(TimeSeries.project_id == id)
        result = await session.execute(query)
        time_series = result.all()
        ts_ids = [item[3] for item in time_series]

        query = update(Project).where(Project.id == id).values(ts_ids=ts_ids, dim=len(ts_ids))
        await session.execute(query)
        await session.commit()

    return [TimeSeriesDTO(ts_name=item[0], len=item[1], ts_description=item[2]) for item in time_series]


async def get_primitives_to_display(project_id: int) -> List[DgPrimitiveToDisplay]:
    res = []
    async with session_factory() as session:
        query = select(FoundPrimitive).where(FoundPrimitive.project_id == project_id)
        result = await session.execute(query)
        found_primitives = result.scalars().all()[0]

        query = select(TimeSeries.id, TimeSeries.name).where(TimeSeries.project_id == project_id)
        result = await session.execute(query)
        time_series = dict(result.all())

        query = select(MatrixProfile).where(MatrixProfile.id.in_(found_primitives.matrix_pr_ids))
        result = await session.execute(query)
        matrix_profiles = result.scalars().all()
        for el in matrix_profiles:
            res.append(DgPrimitiveToDisplay(
                name=f"Матричный профиль({time_series[el.ts_id]})",
                subseqLen=el.subseqLen,
                ts_id=el.ts_id,
                nnDist=el.nnDist,
                key=f"mp{el.id}"
            ))

        query = select(Discord).where(Discord.id.in_(found_primitives.discord_ids))
        result = await session.execute(query)
        discords = result.scalars().all()
        for el in discords:
            for i, idx in enumerate(el.indexes, 1):
                res.append(DgPrimitiveToDisplay(
                    name=f"Диссонанс({time_series[el.ts_id]})_{i}",
                    subseqLen=el.subseqLen,
                    ts_id=el.ts_id,
                    indexes=list(range(idx, idx + el.subseqLen)),
                    key=f"d{el.id}{i}"
                ))

        query = select(Motif).where(Motif.id.in_(found_primitives.motif_ids))
        result = await session.execute(query)
        motifs = result.scalars().all()
        for el in motifs:
            for i in range(len(el.indexes_left)):
                idxl = el.indexes_left[i]
                idxr = el.indexes_right[i]
                res.append(DgPrimitiveToDisplay(
                    name=f"Мотив({time_series[el.ts_id]})_{i+1}",
                    subseqLen=el.subseqLen,
                    ts_id=el.ts_id,
                    indexes=list(range(idxl, idxl + el.subseqLen))+list(range(idxr, idxr + el.subseqLen)),
                    key=f"m{el.id}{i+1}"
                ))

        query = select(Snippet).where(Snippet.id.in_(found_primitives.snippet_ids))
        result = await session.execute(query)
        snippets = result.scalars().all()
        for el in snippets:
            for i, idx in enumerate(el.indexes, 1):
                res.append(DgPrimitiveToDisplay(
                    name=f"Сниппет({time_series[el.ts_id]})_{i}",
                    subseqLen=el.subseqLen,
                    ts_id=el.ts_id,
                    indexes=list(range(idx, idx + el.subseqLen)),
                    key=f"s{el.id}{i}"
                ))

        query = select(Chain).where(Chain.id.in_(found_primitives.chain_ids))
        result = await session.execute(query)
        chains = result.scalars().all()
        iter = 0
        for el in chains:
            for i, num in enumerate(el.numElements, 1):
                indexes = []
                for idx in el.indexes[iter: iter + num]:
                    indexes += list(range(idx, idx + el.subseqLen))
                iter += num
                res.append(DgPrimitiveToDisplay(
                    name=f"Цепочка({time_series[el.ts_id]})_{i}",
                    subseqLen=el.subseqLen,
                    ts_id=el.ts_id,
                    indexes=indexes,
                    key=f"c{el.id}{i}"
                ))

    return res
