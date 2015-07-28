# -*- coding: utf-8 -*-
'''
Unit tests for contacts viewer

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.contacts.views import Configuration, CustomFieldAddModify
from django.utils import six
from lucterios.contacts.models import LegalEntity, Individual, StructureType, \
    Function, Responsability, CustomField, ContactCustomField
from shutil import rmtree
from lucterios.framework.filetools import get_user_dir, readimage_to_base64, \
    get_user_path
from os.path import join, dirname, exists
from lucterios.contacts.views_contacts import IndividualList, LegalEntityList, \
    LegalEntityAddModify, IndividualAddModify, IndividualShow, IndividualUserAdd, \
    IndividualUserValid, LegalEntityDel, LegalEntityShow, ResponsabilityAdd, \
    ResponsabilityModify, LegalEntitySearch, IndividualSearch, \
    LegalEntityListing, LegalEntityLabel, IndividualListing, IndividualLabel
from lucterios.CORE.views_usergroup import UsersEdit
from base64 import b64decode
from lucterios.framework.xfersearch import get_search_query_from_criteria

def change_ourdetail():
    ourdetails = LegalEntity.objects.get(id=1)  # pylint: disable=no-member
    ourdetails.name = "WoldCompany"
    ourdetails.address = "Place des cocotiers"
    ourdetails.postal_code = "97200"
    ourdetails.city = "FORT DE FRANCE"
    ourdetails.country = "MARTINIQUE"
    ourdetails.tel1 = "01-23-45-67-89"
    ourdetails.email = "mr-sylvestre@worldcompany.com"
    ourdetails.save()

def create_jack(empty_user=None):
    empty_contact = Individual()
    empty_contact.firstname = "jack"
    empty_contact.lastname = "MISTER"
    empty_contact.address = "rue de la liberté"
    empty_contact.postal_code = "97250"
    empty_contact.city = "LE PRECHEUR"
    empty_contact.country = "MARTINIQUE"
    empty_contact.tel2 = "02-78-45-12-95"
    empty_contact.email = "jack@worldcompany.com"
    empty_contact.user = empty_user
    empty_contact.save()
    return empty_contact

class ContactsTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        change_ourdetail()
        rmtree(get_user_dir(), True)
        StructureType.objects.create(name="Type A")  # pylint: disable=no-member
        StructureType.objects.create(name="Type B")  # pylint: disable=no-member
        StructureType.objects.create(name="Type C")  # pylint: disable=no-member
        Function.objects.create(name="President")  # pylint: disable=no-member
        Function.objects.create(name="Secretaire")  # pylint: disable=no-member
        Function.objects.create(name="Tresorier")  # pylint: disable=no-member
        Function.objects.create(name="Troufion")  # pylint: disable=no-member
        create_jack()

    def test_individual(self):
        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_comp_equal('COMPONENTS/EDIT[@name="filter"]', None, (1, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="individual"]', (0, 3, 2, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualAddModify')
        self.assert_count_equal('COMPONENTS/*', 25)

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {"address":'Avenue de la Paix{[newline]}BP 987', \
                        "comment":'no comment', "firstname":'Marie', "lastname":'DUPOND', \
                        "city":'ST PIERRE', "country":'MARTINIQUE', "tel2":'06-54-87-19-34', "SAVE":'YES', \
                        "tel1":'09-96-75-15-00', "postal_code":'97250', "email":'marie.dupond@worldcompany.com', \
                        "genre":"2"}, False)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 2)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {'filter':'e'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 2)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {'filter':'marie'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {'filter':'dupon'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {'filter':'jack'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualList()
        self.call('/lucterios.contacts/individualList', {'filter':'truc'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 0)

    def test_individual_image(self):
        self.assertFalse(exists(get_user_path('contacts', 'Image_2.jpg')))
        logo_path = join(dirname(__file__), 'help', 'EditIndividual.png')
        logo_stream = "image.png;" + readimage_to_base64(logo_path, False).decode("utf-8")

        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="logoimg"]', "lucterios.contacts/images/NoImage.png")

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {"SAVE":'YES', 'individual':'2', "uploadlogo":logo_stream}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'individualAddModify')
        self.assertTrue(exists(get_user_path('contacts', 'Image_2.jpg')))

        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="logoimg"]', "data:image/*;base64,", True)

    def test_individual_user(self):
        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_count_equal('COMPONENTS/*', 29)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="genre"]', "Homme")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="firstname"]', "jack")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lastname"]', "MISTER")
        self.assert_xml_equal('COMPONENTS/LINK[@name="email"]', "jack@worldcompany.com")

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="user"]', "---", (2, 8, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="userbtn"]', (4, 8, 1, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="userbtn"]/ACTIONS/ACTION', (None, 'images/add.png', 'lucterios.contacts', 'individualUserAdd', 0, 1, 1))

        self.factory.xfer = IndividualUserAdd()
        self.call('/lucterios.contacts/individualUserAdd', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualUserAdd')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_comp_equal('COMPONENTS/EDIT[@name="username"]', None, (2, 0, 1, 1))
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'lucterios.contacts', 'individualUserValid', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.factory.xfer = IndividualUserValid()
        self.call('/lucterios.contacts/individualUserValid', {'individual':'2', 'username':'jacko'}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'individualUserValid')
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="individual"]', "2")
        self.assert_xml_equal('CONTEXT/PARAM[@name="username"]', "jacko")
        self.assert_count_equal('ACTION', 1)
        self.assert_action_equal('ACTION', (None, None, "CORE", "usersEdit", 1, 1, 1, {"user_actif":"2", "IDENT_READ":"YES"}))
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'individual':'2', 'username':'jacko', 'user_actif':'2', 'IDENT_READ':'YES'}, False)
        self.assert_observer('Core.Custom', 'CORE', 'usersEdit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="username"]', "jacko")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="first_name"]', "jack")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="last_name"]', "MISTER")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="email"]', "jack@worldcompany.com")

        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="user"]', "jacko", (2, 8, 2, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="userbtn"]/ACTIONS/ACTION', (None, 'images/edit.png', 'CORE', 'usersEdit', 0, 1, 1))

    def test_individual_search(self):
        fieldnames = Individual.get_search_fields()
        self.assertEqual(14, len(fieldnames))

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {"address":'Avenue de la Paix{[newline]}BP 987', \
                        "comment":'no comment', "firstname":'Marie', "lastname":'DUPOND', \
                        "city":'ST PIERRE', "country":'MARTINIQUE', "tel2":'06-54-87-19-34', "SAVE":'YES', \
                        "tel1":'09-96-75-15-00', "postal_code":'97250', "email":'marie.dupond@worldcompany.com', \
                        "genre":"2"}, False)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', None)
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 2)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {'CRITERIA':'genre||8||1;2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'genre||8||1;2')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 2)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {'CRITERIA':'genre||8||1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'genre||8||1')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {'CRITERIA':'genre||8||2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'genre||8||2')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {'CRITERIA':'responsability_set.functions||9||1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'responsability_set.functions||9||1')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 0)

        self.factory.xfer = IndividualSearch()
        self.call('/lucterios.contacts/individualSearch', {'CRITERIA':'user.username||5||empt'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualSearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'user.username||5||empt')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 0)

    def test_individual_listing(self):
        self.factory.xfer = IndividualListing()
        self.call('/lucterios.contacts/individualListing', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblPrintMode"]', "{[b]}Type de rapport{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 2)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblMODEL"]', "{[b]}modèle{[/b]}", (0, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "3", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = IndividualListing()
        self.call('/lucterios.contacts/individualListing', {'PRINT_MODE':'4', 'MODEL':3}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'individualListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes physiques'))
        self.assert_attrib_equal('PRINT', 'mode', '4')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 7, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Personnes physiques"')
        self.assertEqual(content_csv[3].strip(), '"prénom";"nom";"adresse";"ville";"tel";"courriel";')

        self.factory.xfer = IndividualListing()
        self.call('/lucterios.contacts/individualListing', {'PRINT_MODE':'4', 'MODEL':3, 'filter':'marie'}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'individualListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes physiques'))
        self.assert_attrib_equal('PRINT', 'mode', '4')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 6, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Personnes physiques"')
        self.assertEqual(content_csv[3].strip(), '"prénom";"nom";"adresse";"ville";"tel";"courriel";')

    def test_individual_label(self):
        self.factory.xfer = IndividualLabel()
        self.call('/lucterios.contacts/individualLabel', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblPrintMode"]', "{[b]}Type de rapport{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 1)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblLABEL"]', "{[b]}étiquette{[/b]}", (0, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="LABEL"]', "1", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="LABEL"]/CASE', 6)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblFIRSTLABEL"]', "{[b]}N° première étiquette{[/b]}", (0, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="FIRSTLABEL"]', "1", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblMODEL"]', "{[b]}modèle{[/b]}", (0, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "4", (1, 3, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = IndividualLabel()
        self.call('/lucterios.contacts/individualLabel', {'PRINT_MODE':'3', 'LABEL': 3, 'FIRSTLABEL':5, 'MODEL':4, 'name_filter':'marie'}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'individualLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes physiques'))
        self.assert_attrib_equal('PRINT', 'mode', '3')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

        self.factory.xfer = IndividualLabel()
        self.call('/lucterios.contacts/individualLabel', {'PRINT_MODE':'3', 'LABEL': 2, 'FIRSTLABEL':4, 'MODEL':4}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'individualLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes physiques'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes physiques'))
        self.assert_attrib_equal('PRINT', 'mode', '3')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def test_individual_fieldsprint(self):
        # pylint: disable=line-too-long
        ourdetails = LegalEntity.objects.get(id=1)  # pylint: disable=no-member
        indiv_jack = Individual.objects.get(id=2)  # pylint: disable=no-member
        resp = Responsability.objects.create(individual=indiv_jack, legal_entity=ourdetails)  # pylint: disable=no-member
        resp.functions = Function.objects.filter(id__in=[1, 2])  # pylint: disable=no-member
        resp.save()

        print_field_list = Individual.get_all_print_fields()
        self.assertEqual(33, len(print_field_list))
        print_text = ""

        for print_field_item in print_field_list:
            print_text += "#%s " % print_field_item[1]
        self.assertEqual("#firstname #lastname #address #postal_code #city #country #tel1 #tel2 #email #comment ", print_text[:86])
        self.assertEqual("#user.username #responsability_set.legal_entity.name #responsability_set.legal_entity.structure_type.name ", print_text[86:192])
        self.assertEqual("#responsability_set.legal_entity.address #responsability_set.legal_entity.postal_code #responsability_set.legal_entity.city #responsability_set.legal_entity.country ", print_text[192:357])
        self.assertEqual("#responsability_set.legal_entity.tel1 #responsability_set.legal_entity.tel2 #responsability_set.legal_entity.email ", print_text[357:472])
        self.assertEqual("#responsability_set.legal_entity.comment #responsability_set.legal_entity.identify_number #responsability_set.functions.name ", print_text[472:597])
        self.assertEqual("#OUR_DETAIL.name #OUR_DETAIL.address #OUR_DETAIL.postal_code #OUR_DETAIL.city #OUR_DETAIL.country ", print_text[597:695])
        self.assertEqual("#OUR_DETAIL.tel1 #OUR_DETAIL.tel2 #OUR_DETAIL.email ", print_text[695:747])
        self.assertEqual("#OUR_DETAIL.comment #OUR_DETAIL.identify_number ", print_text[747:795])
        self.assertEqual("jack MISTER rue de la liberté 97250 LE PRECHEUR MARTINIQUE  02-78-45-12-95 jack@worldcompany.com   WoldCompany  Place des cocotiers 97200 FORT DE FRANCE MARTINIQUE 01-23-45-67-89  mr-sylvestre@worldcompany.com   President{[br/]}Secretaire ", indiv_jack.evaluate(print_text[:597]))
        self.assertEqual("WoldCompany Place des cocotiers 97200 FORT DE FRANCE MARTINIQUE 01-23-45-67-89  mr-sylvestre@worldcompany.com   ", indiv_jack.evaluate(print_text[597:]))

    def test_legalentity(self):
        self.factory.xfer = LegalEntityList()
        self.call('/lucterios.contacts/legalEntityList', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityList')
        self.assert_comp_equal('COMPONENTS/SELECT[@name="structure_type"]', '0', (1, 2, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="structure_type"]/CASE', 4)
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="legal_entity"]', (0, 3, 2, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)

        self.factory.xfer = LegalEntityAddModify()
        self.call('/lucterios.contacts/legalEntityAddModify', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityAddModify')
        self.assert_count_equal('COMPONENTS/*', 25)

        self.factory.xfer = LegalEntityAddModify()
        self.call('/lucterios.contacts/legalEntityAddModify', {"address":'Avenue de la Paix{[newline]}BP 987', \
                        "comment":'no comment', "name":'truc-muche', \
                        "city":'ST PIERRE', "country":'MARTINIQUE', "tel2":'06-54-87-19-34', "SAVE":'YES', \
                        "tel1":'09-96-75-15-00', "postal_code":'97250', "email":'contact@truc-muche.org', \
                        "structure_type":2}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'legalEntityAddModify')

        self.factory.xfer = LegalEntityList()
        self.call('/lucterios.contacts/legalEntityList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 2)
        self.factory.xfer = LegalEntityList()
        self.call('/lucterios.contacts/legalEntityList', {"structure_type":1}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 0)
        self.factory.xfer = LegalEntityList()
        self.call('/lucterios.contacts/legalEntityList', {"structure_type":2}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)
        self.factory.xfer = LegalEntityList()
        self.call('/lucterios.contacts/legalEntityList', {"structure_type":3}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 0)

    def test_legalentity_delete(self):
        self.factory.xfer = LegalEntityDel()
        self.call('/lucterios.contacts/legalEntityDel', {'legal_entity':'1'}, False)
        self.assert_observer('CORE.Exception', 'lucterios.contacts', 'legalEntityDel')
        self.assert_xml_equal("EXCEPTION/MESSAGE", "Vous ne pouvez supprimer cette structure morale!")

    def test_legalentity_responsability(self):
        self.factory.xfer = LegalEntityShow()
        self.call('/lucterios.contacts/legalEntityShow', {'legal_entity':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', "WoldCompany")
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/ACTIONS/ACTION', 3)

        self.factory.xfer = ResponsabilityAdd()
        self.call('/lucterios.contacts/responsabilityAdd', {'legal_entity':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'responsabilityAdd')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="legal_entity"]', "WoldCompany")
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/ACTIONS/ACTION', 3)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="individual"]/RECORD[1]', 'id', '2')

        self.factory.xfer = ResponsabilityAdd()
        self.call('/lucterios.contacts/responsabilityAdd', {'legal_entity':'1', 'name_filter':'jack'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'responsabilityAdd')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="legal_entity"]', "WoldCompany")
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/ACTIONS/ACTION', 3)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="individual"]/RECORD[1]', 'id', '2')

        self.factory.xfer = ResponsabilityModify()
        self.call('/lucterios.contacts/responsabilityModify', {'legal_entity':'1', 'individual':'2', "SAVE":"YES"}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'responsabilityModify')

        self.factory.xfer = LegalEntityShow()
        self.call('/lucterios.contacts/legalEntityShow', {'legal_entity':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', "WoldCompany")
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/RECORD', 1)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]', 'id', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]/VALUE[@name="individual"]', "MISTER jack")
        self.assert_xml_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]/VALUE[@name="functions"]', None)

        self.factory.xfer = ResponsabilityModify()
        self.call('/lucterios.contacts/responsabilityModify', {'responsability':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'responsabilityModify')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="legal_entity"]', "WoldCompany")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="individual"]', "MISTER jack")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_functions"]', "{[b]}fonctions{[/b]}")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="hd_functions_available"]', "{[center]}{[i]}Fonctions disponibles{[/i]}{[/center]}")
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="functions_available"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="hd_functions_chosen"]', "{[center]}{[i]}Fonctions choisies{[/i]}{[/center]}")
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="functions_chosen"]', None)

        self.factory.xfer = LegalEntityShow()
        self.call('/lucterios.contacts/legalEntityShow', {'legal_entity':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/RECORD', 1)

        self.factory.xfer = ResponsabilityModify()
        self.call('/lucterios.contacts/responsabilityModify', {'responsability':'1', 'functions':'2;4', "SAVE":"YES"}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'responsabilityModify')

        self.factory.xfer = LegalEntityShow()
        self.call('/lucterios.contacts/legalEntityShow', {'legal_entity':'1'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', "WoldCompany")
        self.assert_count_equal('COMPONENTS/GRID[@name="responsability"]/RECORD', 1)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]', 'id', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]/VALUE[@name="individual"]', "MISTER jack")
        self.assert_xml_equal('COMPONENTS/GRID[@name="responsability"]/RECORD[1]/VALUE[@name="functions"]', "Secretaire{[br/]}Troufion")

    def test_legalentity_search(self):
        self.factory.xfer = LegalEntityAddModify()
        self.call('/lucterios.contacts/legalEntityAddModify', {"address":'Avenue de la Paix{[newline]}BP 987', \
                        "comment":'no comment', "name":'truc-muche', \
                        "city":'ST PIERRE', "country":'MARTINIQUE', "tel2":'06-54-87-19-34', "SAVE":'YES', \
                        "tel1":'09-96-75-15-00', "postal_code":'97250', "email":'contact@truc-muche.org', \
                        "structure_type":2}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'legalEntityAddModify')

        self.factory.xfer = LegalEntitySearch()
        self.call('/lucterios.contacts/legalEntitySearch', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntitySearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', None)
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 2)

        self.factory.xfer = LegalEntitySearch()
        self.call('/lucterios.contacts/legalEntitySearch', {'searchSelector':'name', 'searchOperator':'5', 'searchValueStr':'truc', 'ACT':'ADD'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntitySearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'name||5||truc')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)

        self.factory.xfer = LegalEntitySearch()
        self.call('/lucterios.contacts/legalEntitySearch', {'searchSelector':'structure_type', 'searchOperator':'8', 'searchValueList':'2', 'ACT':'ADD'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntitySearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'structure_type||8||2')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)

        self.factory.xfer = LegalEntitySearch()
        self.call('/lucterios.contacts/legalEntitySearch', {'CRITERIA':'name||5||truc//structure_type||8||2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntitySearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'name||5||truc//structure_type||8||2')
        self.assert_count_equal('COMPONENTS/*', 20)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)

        self.factory.xfer = LegalEntitySearch()
        self.call('/lucterios.contacts/legalEntitySearch', {'CRITERIA':'name||5||truc//structure_type||8||2', 'ACT':'0'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntitySearch')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CRITERIA"]', 'structure_type||8||2')
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_count_equal('COMPONENTS/GRID[@name="legal_entity"]/RECORD', 1)

    def test_legalentity_listing(self):
        self.factory.xfer = LegalEntityListing()
        self.call('/lucterios.contacts/legalEntityListing', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblPrintMode"]', "{[b]}Type de rapport{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 2)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblMODEL"]', "{[b]}modèle{[/b]}", (0, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "1", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = LegalEntityListing()
        self.call('/lucterios.contacts/legalEntityListing', {'PRINT_MODE':'4', 'MODEL':1}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'legalEntityListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes morales'))
        self.assert_attrib_equal('PRINT', 'mode', '4')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 7, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Personnes morales"')
        self.assertEqual(content_csv[3].strip(), '"nom";"adresse";"ville";"tel";"courriel";')

        self.factory.xfer = LegalEntityListing()
        self.call('/lucterios.contacts/legalEntityListing', {'PRINT_MODE':'4', 'MODEL':1, 'structure_type':2}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'legalEntityListing')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes morales'))
        self.assert_attrib_equal('PRINT', 'mode', '4')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 6, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Personnes morales"')
        self.assertEqual(content_csv[3].strip(), '"nom";"adresse";"ville";"tel";"courriel";')

    def test_legalentity_label(self):
        self.factory.xfer = LegalEntityLabel()
        self.call('/lucterios.contacts/legalEntityLabel', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'legalEntityLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblPrintMode"]', "{[b]}Type de rapport{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 1)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblLABEL"]', "{[b]}étiquette{[/b]}", (0, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="LABEL"]', "1", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="LABEL"]/CASE', 6)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblFIRSTLABEL"]', "{[b]}N° première étiquette{[/b]}", (0, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="FIRSTLABEL"]', "1", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblMODEL"]', "{[b]}modèle{[/b]}", (0, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "2", (1, 3, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = LegalEntityLabel()
        self.call('/lucterios.contacts/legalEntityLabel', {'PRINT_MODE':'3', 'LABEL': 1, 'FIRSTLABEL':3, 'MODEL':2, 'structure_type':2}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'legalEntityLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes morales'))
        self.assert_attrib_equal('PRINT', 'mode', '3')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

        self.factory.xfer = LegalEntityLabel()
        self.call('/lucterios.contacts/legalEntityLabel', {'PRINT_MODE':'3', 'LABEL': 5, 'FIRSTLABEL':2, 'MODEL':2}, False)
        self.assert_observer('Core.Print', 'lucterios.contacts', 'legalEntityLabel')
        self.assert_xml_equal('TITLE', six.text_type('Personnes morales'))
        self.assert_xml_equal('PRINT/TITLE', six.text_type('Personnes morales'))
        self.assert_attrib_equal('PRINT', 'mode', '3')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def test_custom_fields(self):
        self.factory.xfer = Configuration()
        self.call('/lucterios.contacts/configuration', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'configuration')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_count_equal('COMPONENTS/GRID[@name="custom_field"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/HEADER[@name="name"]', "nom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/HEADER[@name="model_title"]', "modèle")
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/HEADER[@name="kind"]', "type")
        self.assert_count_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD', 0)

        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'customFieldAddModify')
        self.assert_xml_equal('TITLE', 'Ajouter un champ personnalisé')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'lucterios.contacts', 'customFieldAddModify', 1, 1, 1, {"SAVE":"YES"}))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('COMPONENTS/*', 17)
        self.assert_comp_equal('COMPONENTS/EDIT[@name="name"]', None, (2, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', None, (2, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="kind"]', '0', (2, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/CHECK[@name="args_multi"]', '0', (2, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="args_min"]', '0', (2, 4, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="args_max"]', '0', (2, 5, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="args_prec"]', '0', (2, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/EDIT[@name="args_list"]', None, (2, 7, 1, 1))

    def test_custom_fields_added(self):
        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {"SAVE":"YES", 'name':'aaa', 'modelname':'contacts.AbstractContact', \
                                                               'kind':'0', 'args_multi':'0', 'args_min':'0', 'args_max':'0', 'args_prec':'0', 'args_list':''}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {"SAVE":"YES", 'name':'bbb', 'modelname':'contacts.AbstractContact', \
                                                               'kind':'1', 'args_multi':'0', 'args_min':'0', 'args_max':'100', 'args_prec':'0', 'args_list':''}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {"SAVE":"YES", 'name':'ccc', 'modelname':'contacts.AbstractContact', \
                                                               'kind':'2', 'args_multi':'0', 'args_min':'-10.0', 'args_max':'10.0', 'args_prec':'1', 'args_list':''}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {"SAVE":"YES", 'name':'ddd', 'modelname':'contacts.LegalEntity', \
                                                               'kind':'3', 'args_multi':'0', 'args_min':'0', 'args_max':'0', 'args_prec':'0', 'args_list':''}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = CustomFieldAddModify()
        self.call('/lucterios.contacts/customFieldAddModify', {"SAVE":"YES", 'name':'eee', 'modelname':'contacts.Individual', \
                                                               'kind':'4', 'args_multi':'0', 'args_min':'0', 'args_max':'0', 'args_prec':'0', 'args_list':'U,V,W,X,Y,Z'}, False)
        self.assert_observer('Core.Acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = Configuration()
        self.call('/lucterios.contacts/configuration', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[1]/VALUE[@name="name"]', 'aaa')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[1]/VALUE[@name="model_title"]', 'contact générique')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[1]/VALUE[@name="kind"]', 'Chaîne')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[2]/VALUE[@name="name"]', 'bbb')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[2]/VALUE[@name="model_title"]', 'contact générique')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[2]/VALUE[@name="kind"]', 'Entier')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[3]/VALUE[@name="name"]', 'ccc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[3]/VALUE[@name="model_title"]', 'contact générique')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[3]/VALUE[@name="kind"]', 'Réel')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[4]/VALUE[@name="name"]', 'ddd')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[4]/VALUE[@name="model_title"]', 'personne morale')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[4]/VALUE[@name="kind"]', 'Booléen')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[5]/VALUE[@name="name"]', 'eee')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[5]/VALUE[@name="model_title"]', 'personne physique')
        self.assert_xml_equal('COMPONENTS/GRID[@name="custom_field"]/RECORD[5]/VALUE[@name="kind"]', 'Sélection')

    def _initial_custom_values(self):
        # pylint: disable=no-self-use
        initial_values = [{'name':'aaa', 'modelname':'contacts.AbstractContact', 'kind':'0', 'args':"{'multi':False, 'min':0, 'max':0, 'prec':0, 'list':[]}"},
                          {'name':'bbb', 'modelname':'contacts.AbstractContact', 'kind':'1', 'args':"{'multi':False,'min':0, 'max':100, 'prec':0, 'list':[]}"},
                          {'name':'ccc', 'modelname':'contacts.AbstractContact', 'kind':'2', 'args':"{'multi':False,'min':-10.0, 'max':10.0, 'prec':1, 'list':[]}"},
                          {'name':'ddd', 'modelname':'contacts.LegalEntity', 'kind':'3', 'args':"{'multi':False,'min':0, 'max':0, 'prec':0, 'list':[]}"},
                          {'name':'eee', 'modelname':'contacts.Individual', 'kind':'4', 'args':"{'multi':False,'min':0, 'max':0, 'prec':0, 'list':['U','V','W','X','Y','Z']}"},
                          {'name':'fff', 'modelname':'contacts.Individual', 'kind':'0', 'args':"{'multi':True,'min':0, 'max':0, 'prec':0, 'list':[]}"}]
        for initial_value in initial_values:
            CustomField.objects.create(**initial_value)  # pylint: disable=no-member

    def test_custom_fields_individual(self):
        self._initial_custom_values()

        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_count_equal('COMPONENTS/*', 39)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_1"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_2"]', "0")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_3"]', "0.0")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_5"]', "U")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_6"]', None)

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualAddModify')
        self.assert_count_equal('COMPONENTS/*', 35)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="custom_1"]', None)
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="custom_2"]', "0")
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="custom_3"]', "0.0")
        self.assert_xml_equal('COMPONENTS/SELECT[@name="custom_5"]', "0")
        self.assert_xml_equal('COMPONENTS/MEMO[@name="custom_6"]', None)

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {'individual':'2', "SAVE":"YES", "custom_1":'blabla', "custom_2":"15", \
                                                              "custom_3":"-5.4", "custom_5":"4", "custom_6":"azerty{[br/]}qwerty"}, False)

        self.factory.xfer = IndividualShow()
        self.call('/lucterios.contacts/individualShow', {'individual':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.contacts', 'individualShow')
        self.assert_count_equal('COMPONENTS/*', 39)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_1"]', 'blabla')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_2"]', "15")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_3"]', "-5.4")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_5"]', "Y")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="custom_6"]', "azerty{[br/]}qwerty")

    def test_custom_fields_printing(self):
        self._initial_custom_values()

        self.factory.xfer = IndividualAddModify()
        self.call('/lucterios.contacts/individualAddModify', {'individual':'2', "SAVE":"YES", "custom_1":'boum!', "custom_2":"-67", "custom_3":"9.9", "custom_5":"2", "custom_6":"a{[br/]}z"}, False)

        print_field_list = Individual.get_all_print_fields()
        self.assertEqual(46, len(print_field_list))
        print_text = ""
        for print_field_item in print_field_list:
            if 'custom_' in print_field_item[1]:
                print_text += "#%s " % print_field_item[1]
        self.assertEqual("#responsability_set.legal_entity.custom_1 #responsability_set.legal_entity.custom_2 ", print_text[:84])
        self.assertEqual("#responsability_set.legal_entity.custom_3 #responsability_set.legal_entity.custom_4 ", print_text[84:168])
        self.assertEqual("#OUR_DETAIL.custom_1 #OUR_DETAIL.custom_2 #OUR_DETAIL.custom_3 #OUR_DETAIL.custom_4 ", print_text[168:252])
        self.assertEqual("#custom_1 #custom_2 #custom_3 #custom_5 #custom_6 ", print_text[252:])

        indiv_jack = Individual.objects.get(id=2)  # pylint: disable=no-member
        self.assertEqual(" 0 0.0 Non ", indiv_jack.evaluate(print_text[168:252]))
        self.assertEqual("boum! -67 9.9 W a{[br/]}z ", indiv_jack.evaluate(print_text[252:]))

    def test_custom_fields_search(self):
        from django.db.models import Q
        self._initial_custom_values()
        custom_1 = ContactCustomField.objects.get_or_create(contact_id=2, field_id=1)  # pylint: disable=no-member
        custom_1[0].value = "pas beau!!!"
        custom_1[0].save()

        fieldnames = Individual.get_search_fields()
        self.assertEqual(19, len(fieldnames))
        self.assertEqual('custom_1', fieldnames[-8][0])
        self.assertEqual('custom_2', fieldnames[-7][0])
        self.assertEqual('custom_3', fieldnames[-6][0])
        self.assertEqual('custom_5', fieldnames[-5][0])
        self.assertEqual('custom_6', fieldnames[-4][0])

        filter_result, desc_result = get_search_query_from_criteria("", Individual)
        self.assertEqual({}, desc_result)
        self.assertEqual(six.text_type(Q()), six.text_type(filter_result))

        filter_result, desc_result = get_search_query_from_criteria("custom_1||5||beau", Individual)
        self.assertEqual({'0':'{[b]}aaa{[/b]} contiens {[i]}"beau"{[/i]}'}, desc_result)
        q_res = Q(contactcustomfield__field__id=1) & Q(**{'contactcustomfield__value__contains':'beau'})
        self.assertEqual(six.text_type(q_res), six.text_type(filter_result))

        find_indiv = list(Individual.objects.filter(q_res))  # pylint: disable=no-member
        self.assertEqual(1, len(find_indiv), find_indiv)
