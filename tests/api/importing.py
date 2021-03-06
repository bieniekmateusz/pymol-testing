import os
import sys
from pymol import cmd, testing, stored

pdbstr = '''ATOM      1  N   GLY    22      -1.195   0.201  -0.206  1.00  0.00           N  
ATOM      2  CA  GLY    22       0.230   0.318  -0.502  1.00  0.00           C  
ATOM      3  C   GLY    22       1.059  -0.390   0.542  1.00  0.00           C  
ATOM      4  O   GLY    22       0.545  -0.975   1.499  1.00  0.00           O  
ATOM      5  H   GLY    22      -1.558  -0.333   0.660  1.00  0.00           H  
ATOM      6 3HA  GLY    22       0.482   1.337  -0.514  0.00  0.00           H  
ATOM      7  HA  GLY    22       0.434  -0.159  -1.479  1.00  0.00           H  
END
'''

molstr = '''glycine
  ChemPy            3D                             0

  7  6  0  0  1  0  0  0  0  0999 V2000
   -1.1946    0.2011   -0.2061 N   0  0  0  0  0  0  0  0  0  0  0  0
    0.2304    0.3181   -0.5021 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0594   -0.3899    0.5419 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5454   -0.9749    1.4989 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.5576   -0.3329    0.6599 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.4824    1.3374   -0.5137 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.4344   -0.1589   -1.4791 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  5  1  0  0  0  0
  2  3  1  0  0  0  0
  2  6  1  0  0  0  0
  2  7  1  0  0  0  0
  3  4  2  0  0  0  0
M  END
'''

mmodstr = '''     7  gly
  34     2 1     5 1     0 0     0 0     0 0     0 0   -1.195000    0.201000   -0.206000    22G   38  0.00000  0.00000 GLY   N
   3     1 1     3 1     6 1     7 1     0 0     0 0    0.230000    0.318000   -0.502000    22G    2  0.00000  0.00000 GLY   CA
   7     2 1     4 2     0 0     0 0     0 0     0 0    1.059000   -0.390000    0.542000    22G    2  0.00000  0.00000 GLY   C
  15     3 2     0 0     0 0     0 0     0 0     0 0    0.545000   -0.975000    1.499000    22G   75  0.00000  0.00000 GLY   O
  44     1 1     0 0     0 0     0 0     0 0     0 0   -1.558000   -0.333000    0.660000    22G   21  0.00000  0.00000 GLY   H
  41     2 1     0 0     0 0     0 0     0 0     0 0    0.482000    1.337000   -0.514000    22G   21  0.00000  0.00000 GLY  3HA
  41     2 1     0 0     0 0     0 0     0 0     0 0    0.434000   -0.159000   -1.479000    22G   21  0.00000  0.00000 GLY   HA
'''

class TestImporting(testing.PyMOLTestCase):

    @testing.requires('network', 'no_run_all')
    def testFetch(self):
        with testing.mkdtemp() as fetch_path:
            names = []
            cmd.set('fetch_path', fetch_path)
            cmd.set('fetch_host', 'pdb pdbe')

            cmd.fetch('1avy', '1avy1', type='pdb1')
            names += ['1avy1']
            self.assertItemsEqual(cmd.get_names(), names)
            self.assertEqual(cmd.count_states('1avy1'), 3)

            cmd.fetch('1avy', type='2fofc')
            names += ['1avy_2fofc']
            self.assertItemsEqual(cmd.get_names(), names)
            self.assertEqual(cmd.get_type('1avy_2fofc'), 'object:map')

    def testFetchLocal(self):
        try:
            import urllib.parse as urlparse
        except ImportError:
            import urlparse

        # PyMOL 1.8.6 adds full URLs, remove them
        import pymol
        pdbpaths = pymol.importing.hostPaths['pdb']
        pdbpaths[:] = [p for p in pdbpaths if '://' not in p]

        with testing.mkdtemp() as fetch_path:
            names = []
            cmd.set('fetch_path', fetch_path)
            cmd.set('fetch_host', urlparse.urlunsplit(['file', '',
                self.datafile('pdb.mirror'), '', '']))

            cmd.fetch('1avy', type='pdb')
            names += ['1avy']
            self.assertItemsEqual(cmd.get_names(), names)

            cmd.fetch('1avyB', type='pdb')
            names += ['1avyB']
            self.assertItemsEqual(cmd.get_names(), names)
            self.assertEqual(cmd.get_chains('1avyB'), ['B'])

            cmd.fetch('1aq5', type='pdb', multiplex=1)
            names += ['1aq5_%04d' % (i+1) for i in range(20)]
            self.assertItemsEqual(cmd.get_names(), names)

    def testFinishObject(self):
        cmd.finish_object
        self.skipTest("TODO")

    def testLoad(self):
        cmd.load
        self.skipTest("TODO")

    @testing.requires_version('1.7.3.0')
    def testLoad_idx(self):
        cmd.load(self.datafile('desmond/Bace_mapper_20143_3a51a59_e85111a_solvent_11_replica0-out.idx'))
        self.assertEqual(cmd.count_states(), 210)
        self.assertEqual(cmd.count_atoms(), 2482)

    def testLoad_pqr(self):
        cmd.load(self.datafile('example.pqr'))
        charges = []
        radii = []
        n = cmd.iterate('all', 'charges.append(partial_charge);radii.append(elec_radius)', space=locals())
        self.assertEqual(n, 191)
        self.assertTrue(any(x != 0.0 for x in charges))
        self.assertTrue(any(x != 0.0 for x in radii))

    @testing.requires_version('2.2')
    def testLoad_pqr_various(self):
        import glob
        pqrdir = self.datafile('pqr')
        extent_expect = {
            19: [[1999.32, 2998.77, -901.70], [2008.4, 3006.35, -898.02]],
            36: [[1998.629, 2998.033, -902.509], [2008.765, 3006.347, -898.022]],
        }
        for filename in glob.glob(os.path.join(pqrdir, '*.pqr')):
            cmd.load(filename)
            n_atom = cmd.count_atoms()
            extent = cmd.get_extent()
            self.assertArrayEqual(extent, extent_expect[n_atom], delta=1e-2, msg=filename)
            if 'chain' in os.path.basename(filename):
                self.assertEqual(cmd.get_chains(), ['A'])
            else:
                self.assertEqual(cmd.get_chains(), [''])
            cmd.delete('*')

    @testing.foreach.product(
            ['sdf', 'mol2', 'xyz', 'pdb', 'mmd'],
            [0, 1],
            )
    def testLoad_multi(self, ext, discrete):
        '''
        Load multi-state files with discrete=0/1 and multiplex=0/1
        '''
        N = 10
        filename = self.datafile('ligs3d.' + ext)

        # mutiplex=0
        cmd.load(filename, discrete=discrete, multiplex=0)
        self.assertEqual(cmd.count_discrete('*'), discrete)
        self.assertEqual(cmd.count_states(), N)
        self.assertEqual(len(cmd.get_object_list()), 1)

        if ext in ['mmd']:
            return

        # mutiplex=1
        cmd.delete('*')
        cmd.load(filename, discrete=discrete, multiplex=1)
        self.assertEqual(cmd.count_discrete('*'), discrete * N)
        self.assertEqual(cmd.count_states(), 1)
        self.assertEqual(len(cmd.get_object_list()), N)

    @testing.foreach(
            ['.ccp4', True],
            ['.brix', True],
            ['.spi', False],
            )
    @testing.requires_version('1.7.3.0')
    def testLoad_map(self, ext, check_extent):
        filename = self.datafile('emd_1155' + ext)
        if not os.path.exists(filename):
            self.skipTest("missing " + filename)

        cmd.load(filename, 'map1')
        field = cmd.get_volume_field('map1', copy=0)
        self.assertEqual(field.shape, (141, 91, 281))

        if check_extent:
            extent = cmd.get_extent('map1')
            self.assertArrayEqual(extent, [[0.0, 0.0, 0.0], [2296.0, 1476.0, 4592.0]], delta=1e-2)

    @testing.requires_version('1.7.3.0')
    def testLoad_cube(self):
        cmd.load(self.datafile('h2o-elf.cube'))
        extent = cmd.get_extent('h2o-elf')
        self.assertArrayEqual(extent, [
            [  -0.075,  -0.075,  -0.075],
            [   5.925,   5.925,   5.925]], delta=1e3)
        field = cmd.get_volume_field('h2o-elf', copy=0)
        self.assertEqual(field.shape, (40, 40, 40))
        self.assertAlmostEqual(field.mean(), 0.06915, delta=1e-4)

    def _testLoad_dx(self, filename):
        cmd.load(self.datafile(filename), 'map1')
        extent = cmd.get_extent('map1')
        self.assertArrayEqual(extent, [[1.0, 2.0, 3.0], [5.0, 7.0, 9.0]], delta=1e-2)

    def testLoad_dx(self):
        self._testLoad_dx('mapaligned.dx')
        self._testLoad_dx('mapnumeric.dx')

    @testing.requires_version('2.1')
    def testLoad_dx_skewed(self):
        self._testLoad_dx('mapskewed.dx')

    def testLoadBrick(self):
        cmd.load_brick
        self.skipTest("TODO")

    def testLoadCallback(self):
        cmd.load_callback
        self.skipTest("TODO")

    def testLoadCgo(self):
        cmd.load_cgo
        self.skipTest("TODO")

    def testLoadEmbedded(self):
        cmd.load(self.datafile("embed.p1m"))
        self.assertEqual(6, cmd.count_atoms())
        self.assertEqual(2, cmd.count_atoms('elem O'))

    def testLoadMap(self):
        cmd.load_map
        self.skipTest("TODO")

    def testLoadModel(self):
        cmd.fragment('gly')
        m = cmd.get_model()
        cmd.delete('*')
        cmd.load_model(m, 'm1')
        self.assertEqual(7, cmd.count_atoms())

    def testLoadObject(self):
        cmd.load_object
        self.skipTest("TODO")

    def testLoadRaw(self):
        cmd.load_raw(open(self.datafile("sampletrajectory.pdb")).read(), "pdb")
        self.assertEqual(115, cmd.count_atoms())

    @testing.foreach(
            ['.pdb', '.dcd'],
            ['.pdb', '.crd'],
            ['.gro', '.xtc'],
            )
    @testing.requires_version('1.7.3.0')
    def testLoadTraj(self, topext, trjext):
        pdbfile = self.datafile("sampletrajectory" + topext)
        dcdfile = self.datafile("sampletrajectory" + trjext)

        cmd.load(pdbfile)
        cmd.load_traj(dcdfile)
        self.assertEqual(11, cmd.count_states())
        cmd.delete('*')

        cmd.load(pdbfile)
        cmd.load_traj(dcdfile, state=1, interval=2, max=3)
        self.assertEqual(3, cmd.count_states())
        cmd.delete('*')

        cmd.load(pdbfile)
        cmd.load_traj(dcdfile, state=1, start=3, stop=5)
        self.assertEqual(3, cmd.count_states())
        cmd.delete('*')

        cmd.load(pdbfile)
        cmd.load_traj(dcdfile, state=1, stop=9, average=3)
        self.assertEqual(3, cmd.count_states())
        cmd.delete('*')

    @testing.requires_version('1.8.5')
    def testLoadCharmmCor(self):
        # http://www.ks.uiuc.edu/Research/vmd/plugins/molfile/corplugin.html
        for fmt in ['', 'cor']:
            cmd.load(self.datafile("charmm.crd"), format=fmt)
            self.assertEqual(81, cmd.count_atoms(), 'fmt: ' + fmt)
            cmd.delete('*')

    def testLoadTOP(self):
        '''
        Data files from:
        http://ambermd.org/tutorials/basic/tutorial2/section6.htm
        '''
        cmd.load(self.datafile("TRPcage.top"))
        cmd.load_traj(self.datafile("heat1.crd"), "TRPcage")
        self.assertEqual(304, cmd.count_atoms())
        self.assertEqual(10, cmd.count_states())

    @testing.requires_version('1.7.5')
    def testLoadPSF(self):
        cmd.load(self.datafile("ubiquitin.psf"))
        self.assertEqual(26190, cmd.count_atoms())
        self.assertEqual(0, cmd.count_states())

    @testing.requires_version('1.7.5')
    def testLoadVaspCHGCAR(self):
        cmd.load(self.datafile("vasp.CHGCAR"), 'vasp.CHGCAR')
        self.assertEqual(cmd.get_type('vasp.CHGCAR'), 'object:map')
        extend = cmd.get_extent('vasp.CHGCAR')
        self.assertArrayEqual(extend, [[0.0, 0.0, 0.0], [6.5, 6.5, 7.7]], delta=1e-2)

    @testing.requires_version('1.7.5')
    def testLoadVaspOUTCAR(self):
        cmd.load(self.datafile("vasp.OUTCAR"))
        self.assertEqual(2, cmd.count_atoms())
        self.assertEqual(11, cmd.count_states())

    @testing.requires_version('1.7.5')
    def testLoadVaspPOSCAR(self):
        cmd.load(self.datafile("vasp.POSCAR"))
        self.assertEqual(2, cmd.count_atoms())
        self.assertEqual(1, cmd.count_states())

    @testing.requires_version('1.8.5.0')
    def testLoadMSMSSurface(self):
        cmd.load(self.datafile('surface.face'))
        e = cmd.get_extent('surface')
        self.assertArrayEqual(e, [
            [28.003,  25.573,  12.883],
            [34.238,  31.434,  17.835]], delta=1e-3)

    def testReadMmodstr(self):
        cmd.read_mmodstr(mmodstr, 'm1')
        self.assertEqual(7, cmd.count_atoms())

    def testReadMolstr(self):
        cmd.read_molstr(molstr, 'm1')
        self.assertEqual(7, cmd.count_atoms())

    def testReadPdbstr(self):
        cmd.read_pdbstr(pdbstr, 'm1')
        self.assertEqual(7, cmd.count_atoms())

        cmd.read_pdbstr(pdbstr, 'm1')
        self.assertEqual(2, cmd.count_states())

    def testReadSdfstr(self):
        sdfstr = molstr + '$$$$\n'

        cmd.read_sdfstr(sdfstr, 'm1')
        self.assertEqual(7, cmd.count_atoms())

    @testing.requires_version('1.8.3.1')
    def testLoadSDFV3000(self):
        cmd.load(self.datafile("v3000.sdf"))
        self.assertEqual(12, cmd.count_atoms())
        self.assertEqual( 1, cmd.count_atoms('formal_charge = +1'))
        self.assertEqual( 1, cmd.count_atoms('formal_charge = -1'))
        self.assertEqual( 6, cmd.count_atoms('elem C'))
        self.assertEqual( 6, cmd.count_atoms('elem H'))
        self.assertEqual( 4, cmd.count_atoms('(first elem H) extend 2'))

    def testReadXplorstr(self):
        cmd.read_xplorstr
        self.skipTest("TODO")

    def testSetSession(self):
        # see TestExporting.testGetSession
        pass

    def testSpace(self):
        cmd.space('pymol', 0.5)
        cmd.space('cmyk', 0.7)
        cmd.space('rgb')

    @testing.requires_version('1.7.3.0')
    def testLoadCoords(self):
        import numpy
        cmd.fragment('gly', 'm1')
        coords = cmd.get_coords('m1')
        coords += 5.0
        cmd.load_coords(coords, 'm1')
        self.assertTrue(numpy.allclose(coords, cmd.get_coords('m1')))

    @testing.requires_version('1.7.3.0')
    def testLoadCoordset(self):
        import numpy
        cmd.fragment('gly', 'm1')
        coords = cmd.get_coordset('m1')
        cmd.load_coordset(coords, 'm1', state=2)
        self.assertEqual(2, cmd.count_states('m1'))

        # data manipulation with copy=0
        cmd.get_coordset('m1', copy=0)[:] += 5.0
        self.assertTrue(numpy.allclose(coords + 5.0, cmd.get_coords('m1')))

    @testing.requires_version('1.7.7')
    def testLoadPDBML(self):
        cmd.load(self.datafile("1ubq.xml.gz"))
        self.assertEqual(660, cmd.count_atoms())
        symmetry = cmd.get_symmetry()
        self.assertArrayEqual(symmetry[:6], [50.84, 42.77, 28.95, 90.0, 90.0, 90.0], delta=1e-4)
        self.assertEqual(symmetry[6], 'P 21 21 21')

    @testing.requires_version('1.7.7')
    def testLoadCML(self):
        cmd.load(self.datafile("GLY.cml"))
        self.assertEqual(10, cmd.count_atoms())

    @testing.requires_version('1.7.7')
    def testLoadPDBQT(self):
        cmd.set('retain_order')
        cmd.load(self.datafile("NSC7810.pdbqt"))
        charges = []
        n = cmd.iterate('all', 'charges.append(partial_charge)', space=locals())
        self.assertEqual(n, 26)
        charges_expected = [0.002, 0.012, -0.024, 0.012, 0.002, 0.019, 0.052,
                0.002, -0.013, 0.013, -0.013, 0.002, 0.013, -0.024, 0.052,
                0.012, 0.012, 0.002, 0.002, 0.019, 0.21, -0.644, -0.644,
                0.21, -0.644, -0.644]
        self.assertArrayEqual(charges, charges_expected, delta=1e-4)

    @testing.requires_version('1.8.3.1')
    def testLoadPLY(self):
        cmd.load(self.datafile("test_PHE_pentamer.ply.gz"))
        e = cmd.get_extent('test_PHE_pentamer')
        self.assertArrayEqual(e, [[-314.1,-303.6,-280.9], [1592.0,1042.5, 868.0]], delta=1e-3)

    @testing.requires_version('1.8.4')
    def testLoadMMTF(self):
        cmd.load(self.datafile("3njw.mmtf.gz"))
        self.assertEqual(169, cmd.count_atoms())
        self.assertEqual(36, cmd.count_atoms('ss S'))
        self.assertEqual(25, cmd.count_atoms('solvent'))
        symmetry = cmd.get_symmetry()
        self.assertArrayEqual(symmetry[:6], [19.465, 21.432, 29.523, 90.0, 90.0, 90.0], delta=1e-4)
        self.assertEqual(symmetry[6], 'P 21 21 21')

    @testing.requires_version('1.8.4')
    def testLoadMMTFEmpty(self):
        cmd.load(self.datafile("mmtf/empty-all0.mmtf"))
        self.assertEqual(cmd.count_states(), 0)
        cmd.delete('*')

        cmd.load(self.datafile("mmtf/empty-numModels1.mmtf.gz"))
        self.assertEqual(cmd.count_atoms(), 0)
        self.assertEqual(cmd.get_names(), ["empty-numModels1"])
        cmd.delete('*')

        cmd.load(self.datafile("mmtf/empty-numChains1.mmtf.gz"))
        self.assertEqual(cmd.count_atoms(), 0)
        self.assertEqual(cmd.get_names(), ["empty-numChains1"])
        cmd.delete('*')

        cmd.load(self.datafile("mmtf/empty-mmtfVersion99999999.mmtf"))
        self.assertEqual(cmd.get_names(), [])
        cmd.delete('*')

    @testing.foreach(
            ['', '*',                   True],
            ['', 'pdb_header',          True],
            ['', 'x pdb_header y',      True],
            ['', 'other',               False],
            ['',                None,   False],
            ['other',           None,   False],
            ['pdb_header',      None,   True],
            ['x pdb_header y',  None,   True],
            ['*',               None,   True],
            )
    @testing.requires_version('1.8.4')
    @testing.requires('incentive')
    def testPdbHeader(self, load_object_props_default, object_props, truth):
        cmd.set('load_object_props_default', load_object_props_default)
        cmd.load(self.datafile('1rx1.pdb'), 'm1', object_props=object_props)
        self.assertEqual(truth, 'pdb_header' in (cmd.get_property_list('m1') or ()))

    @testing.requires_version('1.7.4')
    def testLoadPWG(self):
        if sys.version_info[0] < 3:
            import urllib2
        else:
            import urllib.request as urllib2

        content_index = b'Hello World\n'
        port = 8084
        baseurl = 'http://localhost:%d' % port

        def urlread(url):
            handle = urllib2.urlopen(url, timeout=3.0)
            try:
                return handle.read()
            finally:
                handle.close()

        with testing.mkdtemp() as rootdir:
            filename = os.path.join(rootdir, 'index.html')
            with open(filename, 'wb') as handle:
                handle.write(content_index)

            filename = os.path.join(rootdir, 'start.pwg')
            with open(filename, 'w') as handle:
                handle.write('root %s\n' % rootdir)
                handle.write('port %d\n' % port)
            cmd.load(filename)

            content = urlread(baseurl)
            self.assertEqual(content, content_index)

            # Warning: can't call locking functions here, will dead-lock
            # get_version is non-locking since 1.7.4

            content = urlread(baseurl + '/apply/pymol.cmd.get_version')
            content = content.decode('ascii', errors='ignore')
            self.assertTrue(content, cmd.get_version()[0] in content)

    @testing.requires_version('2.1')
    def testChemCompCartnUse(self):
        xyz_model = (1., 2., 3.)
        xyz_ideal = (4., 5., 6.)
        xyz_short = (7., 8., 9.)

        for (value, xyz) in [
                (0x00, xyz_ideal),
                (0x01, xyz_ideal),
                (0x02, xyz_model),
                (0x03, xyz_ideal),
                (0x04, xyz_short),
                (0x05, xyz_ideal),
                (0x06, xyz_model),
                (0x07, xyz_ideal),
            ]:
            cmd.set('chem_comp_cartn_use', value)
            cmd.load(self.datafile('chem_comp-fe.cif'), 'm1')
            self.assertArrayEqual(xyz, cmd.get_coords('m1').reshape(-1))
            cmd.delete('*')

    @testing.requires_version('2.1')
    def testCifMissing(self):
        N = 7
        cmd.fragment('gly', 'm1')
        cmd.alter('all', '(chain, segi, resv, alt) = ("?", ".", 5, "")')

        s = cmd.get_str('cif')
        self.assertTrue("'?'" in s or '"?"' in s) # chain
        self.assertTrue("'.'" in s or '"."' in s) # segi
        self.assertTrue(' ? ' in s) # e.g. pdbx_PDB_ins_code
        self.assertTrue(' . ' in s) # e.g. label_alt_id

        cmd.delete('*')
        cmd.set('cif_keepinmemory')
        cmd.load(s, 'm2', format='cifstr')
        self.assertEqual(['?'], cmd.get_chains())
        self.assertEqual(cmd.count_atoms('segi .'), N)
        self.assertEqual(cmd.count_atoms('alt ""'), N)  # no alt
        self.assertEqual(cmd.count_atoms('resi 5'), N)  # no ins_code

        from pymol.querying import cif_get_array
        self.assertEqual(cif_get_array("m2", "_atom_site.type_symbol"), list('NCCOHHH'))
        self.assertEqual(cif_get_array("m2", "_atom_site.id", "i"),     list(range(1, N + 1)))
        self.assertEqual(cif_get_array("m2", "_atom_site.auth_asym_id"),        ['?'] * N)
        self.assertEqual(cif_get_array("m2", "_atom_site.label_asym_id"),       ['.'] * N)
        self.assertEqual(cif_get_array("m2", "_atom_site.pdbx_pdb_ins_code"),   [None] * N)
        self.assertEqual(cif_get_array("m2", "_atom_site.label_alt_id"),        [None] * N)

    @testing.foreach.product((0, 1), (0, 1))
    @testing.requires_version('2.3')
    @testing.requires('incentive')
    def testLoadMae(self, multiplex, discrete):
        cmd.load(self.datafile('multimae.maegz'), 'm',
                multiplex=multiplex, discrete=discrete)

        nstate = 4
        natoms = 79
        nmodel = 1
        ndiscrete = discrete

        if multiplex:
            natoms *= nstate
            ndiscrete *= nstate
            nmodel = nstate
            nstate = 1
        elif discrete:
            self.assertEqual(cmd.count_atoms(state=1), natoms)
            natoms *= nstate

        self.assertEqual(cmd.count_states(), nstate)
        self.assertEqual(cmd.count_discrete('*'), ndiscrete)
        self.assertEqual(cmd.count_atoms(), natoms)
        self.assertEqual(len(cmd.get_object_list()), nmodel)

    @testing.requires_version('2.3')
    @testing.requires('incentive')
    def testLoadMaeUserLabel(self):
        cmd.load(self.datafile('userlabels2.mae'), 'm')
        cmd.iterate('rank 1', 'stored.label = label')
        self.assertEqual(stored.label, '1.31 TRP')
