from .dataset import *
from .loader import *

import torchvision.transforms as transforms


class Loaders:

    def __init__(self, config, transform_train, transform_test):


        self.datasets = ['market_train', 'duke_train', 'market_test', 'duke_test']

        # dataset
        self.market_path = config.market_path
        self.duke_path = config.duke_path
        self.train_dataset = config.train_dataset
        assert self.train_dataset in self.datasets

        # transform
        self.transform_train = transform_train
        self.transform_test = transform_test

        # batch size
        self.p = config.p
        self.k = config.k

        # dataset paths
        self.samples_path = {
            'market_train': os.path.join(self.market_path, 'bounding_box_train/'),
            'duke_train': os.path.join(self.duke_path, 'p3_g_gcn/'),
            'market_test_query': os.path.join(self.market_path, 'query/'),
            'market_test_gallery': os.path.join(self.market_path, 'bounding_box_test/'),
            'duke_test_query': os.path.join(self.duke_path, 'query/'),
            'duke_test_gallery': os.path.join(self.duke_path, 'bounding_box_test/')}

        # load
        self._load()


    def _load(self):

        # train dataset and iter
        train_samples = self._get_train_samples(self.train_dataset)
        self.train_iter = self._get_uniform_iter(train_samples, self.transform_train, self.p, self.k)

        # market test dataset and loader
        market_query_samples, market_gallery_samples = self._get_test_samples('market_test')
        self.market_query_loader = self._get_loader(market_query_samples, self.transform_test, 100)
        self.market_gallery_loader = self._get_loader(market_gallery_samples, self.transform_test, 100)

        # duke test dataset and loader
        duke_query_samples, duke_gallery_samples = self._get_test_samples('duke_test')
        self.duke_query_loader = self._get_loader(duke_query_samples, self.transform_test, 100)
        self.duke_gallery_loader = self._get_loader(duke_gallery_samples, self.transform_test, 100)


    def _get_train_samples(self, train_dataset):

        train_samples_path = self.samples_path[train_dataset]
        if train_dataset == 'market_train':
            samples = Samples4Market(train_samples_path)
        elif train_dataset == 'duke_train':
            samples = Samples4Duke(train_samples_path)

        return samples


    def _get_test_samples(self, test_dataset):

        query_data_path = self.samples_path[test_dataset + '_query']
        gallery_data_path = self.samples_path[test_dataset + '_gallery']

        if test_dataset == 'market_test':
            query_samples = Samples4Market(query_data_path, reorder=False)
            gallery_samples = Samples4Market(gallery_data_path, reorder=False)
        elif test_dataset == 'duke_test':
            query_samples = Samples4Duke(query_data_path, reorder=False)
            gallery_samples = Samples4Duke(gallery_data_path, reorder=False)

        return query_samples, gallery_samples


    def _get_uniform_iter(self, samples, transform, p, k):
        '''
        load person reid data_loader from images_folder
        and uniformly sample according to class
        :param images_folder_path:
        :param transform:
        :param p:
        :param k:
        :return:
        '''
        dataset = PersonReIDDataSet(samples.samples, transform=transform)
        loader = data.DataLoader(dataset, batch_size=p * k, num_workers=8, drop_last=False,
                                 sampler=ClassUniformlySampler(dataset, class_position=1, k=k))
        iters = IterLoader(loader)

        return iters


    def _get_random_iter(self, samples, transform, batch_size):

        dataset = PersonReIDDataSet(samples.samples, transform=transform)
        loader = data.DataLoader(dataset, batch_size=batch_size, num_workers=8, drop_last=False, shuffle=True)
        iters = IterLoader(loader)

        return iters


    def _get_loader(self, samples, transform, batch_size):

        dataset = PersonReIDDataSet(samples.samples, transform=transform)
        loader = data.DataLoader(dataset, batch_size=batch_size, num_workers=8, drop_last=False, shuffle=True)
        return loader

