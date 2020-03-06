# -*- coding: utf-8

import pandas as pd

import dbConMgr, fileConMgr
# from M06_Utility import comUtility


class DataManager:

    def __init__(self, source: str = "file"):

        # 기본 정보
        self._source: str = source
        self._conMgr = None

        # 쿼리 및 파일 Read 결과를 담을 Array 변수들을 선언
        self.df_demand: pd.DataFrame = None
        self.df_prod_wheel: pd.DataFrame = None
        self.df_prod_yield: pd.DataFrame = None

        # Dictionary 변수 선언
        self._dict_prod_yield: dict = {}

    def SetupObject(self):    # or source = "db"
        if self._source == "db":
            self._setup_db_connection()
        elif self._source == "file":
            self._setup_file_connection()

        self.df_demand = self._conMgr.load_data(data_name="demand")
        self.df_prod_wheel = self._conMgr.load_data(data_name="prod_wheel")
        self.df_prod_yield = self._conMgr.load_data(data_name="prod_yield")

        self._preprocessing()

        self._build_dict_prod_yield()

        # comUtility.Utility.SetRootPath(rootPath=self._conMgr.RootPath)
        # comUtility.Utility.SetConfPath(confPath=self._conMgr.conf_path)

    def _setup_db_connection(self):
        self._conMgr = dbConMgr.ConnectionManager()
        self._conMgr.LoadConInfo()

    def _setup_file_connection(self):
        self._conMgr: fileConMgr.FileManager = fileConMgr.FileManager()
        self._conMgr.setup_object()

    def _get_dict_prod_yield(self):
        return self._dict_prod_yield

    def _build_dict_prod_yield(self):
        self._dict_prod_yield: dict = {}
        for idx, row in self.df_prod_yield.iterrows():
            if row['oper'] not in self._dict_prod_yield.keys():
                self._dict_prod_yield[row['oper']] = {row['grade']: row['prod_yield']}
            else:
                if row['grade'] not in self._dict_prod_yield[row['oper']].keys():
                    self._dict_prod_yield[row['oper']][row['grade']] = row['prod_yield']
                else:
                    raise KeyError(
                        "Production Yield 테이블의 키가 중복되었습니다."
                    )

    def _preprocessing(self):

        # Changing dtypes
        self._change_column_dtype(df_name="df_demand", col_name="yyyymm", dtype="str")
        self._change_column_dtype(df_name="df_demand", col_name="qty", dtype="float")

    def _change_column_dtype(self, df_name: str, col_name: str, dtype: str):
        if not self._chk_column_name(column_name=col_name, df_name=df_name):
            raise KeyError(
                f"데이터 프레임 {df_name} 에는 칼럼 [{col_name}] 가 존재하지 않습니다."
            )
        df: pd.DataFrame = self._get_attr(df_name)
        df[col_name] = df[col_name].astype(dtype)

    def _chk_column_name(self, column_name: str, df_name: str = "_df"):
        does_exists: bool = False
        if not self._check_is_df(df_name=df_name):
            return does_exists
        df: pd.DataFrame = self._get_attr(attr=df_name)
        if column_name in df.columns:
            does_exists = True
        return does_exists

    def _check_is_df(self, df_name: str):
        is_df: bool = False
        if not self._chk_exists(attr=df_name):
            return is_df
        attr = self._get_attr(attr=df_name)
        if type(attr) is pd.DataFrame:
            is_df = True
        return is_df

    def _get_attr(self, attr: str):
        attr_obj = None
        if self._chk_exists(attr=attr):
            attr_obj = self.__getattribute__(attr)
        return attr_obj

    def _chk_exists(self, attr: str):
        existence: bool = attr in self.__dict__.keys()
        return existence